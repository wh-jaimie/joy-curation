# -*- coding: utf-8 -*-
"""
조이네영어도서관 - 유아·초등 영어원서 큐레이션 파이프라인
================================================================
도서관 정보나루(data4library.kr) Open API 로 전국 공공도서관 인기대출도서를
수집 → ISBN 접두어로 영어원서만 필터 → 대출횟수 합산 정렬 → 도서 상세정보 결합
→ JSON / CSV(엑셀) 로 저장한다.

사용법:
    1) 아래 AUTH_KEY 에 도서관 정보나루 인증키를 넣는다 (환경변수 D4L_KEY 로도 가능)
    2) python curate_english_books.py
    3) output/ 폴더에 결과 파일 생성

필터 원리:
    영어원서는 ISBN13 이 978-0 / 978-1 로 시작 (영어권 출판).
    한국 도서는 978-89 / 979-11. 이 접두어로 영어원서를 걸러낸다.
"""

import os
import sys
import csv
import json
import time
import argparse
from collections import defaultdict

import requests

# ----------------------------------------------------------------------------
# 설정
# ----------------------------------------------------------------------------
AUTH_KEY = os.environ.get("D4L_KEY", "")  # 도서관 정보나루 인증키: 환경변수 D4L_KEY 로 설정

BASE_URL = "http://data4library.kr/api"

# 유아·초등 대상 연령 구간 (from_age, to_age). API 는 구간별로 나눠 호출한다.
AGE_RANGES = [
    (0, 5),    # 영유아
    (6, 7),    # 유치~취학
    (8, 9),    # 초등 저학년
    (10, 13),  # 초등 중고학년
]

# 영어원서 대출이 많은 영어 특화 도서관. 이름으로 libSrch 조회해 libCode 를 얻는다.
# (도서관 지정 수집 = 전국통합 대신 여기서만 뽑아 영어원서가 순위를 채우게 함)
TARGET_LIBRARY_NAMES = [
    "꿈나래어린이영어도서관",   # 마포
    "영어특성화도서관",         # 양천구
    "용두어린이영어도서관",     # 서울 동대문
    "영어도서관",               # 부산 구포 등 (이름에 '영어도서관' 포함)
    "어린이영어도서관",         # 각지
]

# libCode 를 직접 알고 있으면 여기에 넣으면 조회를 건너뛴다. 예: ["111003", ...]
TARGET_LIB_CODES = []

# 영어원서 판별용 ISBN13 접두어 (영어권 출판)
ENGLISH_ISBN_PREFIXES = ("9780", "9781")

# 수집 파라미터
PAGE_SIZE = 200          # 한 페이지당 도서 수 (최대치 권장)
MAX_PAGES = 10           # 연령대별 최대 페이지 (500건/일 제한 고려해 조절)
REQUEST_DELAY = 0.3      # API 호출 간 대기(초) - 서버 배려
TOP_N = 100              # 최종 큐레이션 상위 권수 (상세조회 대상)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


# ----------------------------------------------------------------------------
# API 호출 헬퍼
# ----------------------------------------------------------------------------
def call_api(endpoint, params):
    """API 를 호출하고 JSON dict 를 반환. 오류 시 None."""
    params = dict(params)
    params["authKey"] = AUTH_KEY
    params["format"] = "json"
    url = f"{BASE_URL}/{endpoint}"
    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as e:
        print(f"  [!] 요청 실패 ({endpoint}): {e}", file=sys.stderr)
        return None

    # API 레벨 오류 (활성화 안 됨 등)
    if isinstance(data.get("response"), dict) and data["response"].get("error"):
        print(f"  [!] API 오류: {data['response'].get('error')} "
              f"(code={data['response'].get('errCode')})", file=sys.stderr)
        return None
    return data


def is_english_original(isbn13):
    """ISBN13 접두어로 영어원서 여부 판별."""
    if not isbn13:
        return False
    isbn = isbn13.replace("-", "").strip()
    return isbn.startswith(ENGLISH_ISBN_PREFIXES)


# ----------------------------------------------------------------------------
# 0단계: 영어 특화 도서관 libCode 조회
# ----------------------------------------------------------------------------
def resolve_library_codes():
    """TARGET_LIBRARY_NAMES 를 libSrch 로 조회해 libCode 목록을 만든다.
    TARGET_LIB_CODES 가 채워져 있으면 그대로 사용한다.
    반환: [(libCode, libName), ...]
    """
    if TARGET_LIB_CODES:
        return [(code, "") for code in TARGET_LIB_CODES]

    print("[도서관] 영어 특화 도서관 libCode 조회...")
    found = {}  # libCode -> libName
    for name in TARGET_LIBRARY_NAMES:
        data = call_api("libSrch", {"libName": name, "pageSize": 100})
        if not data:
            continue
        libs = data.get("response", {}).get("libs", [])
        for item in libs:
            lib = item.get("lib", {})
            code = str(lib.get("libCode", "")).strip()
            libname = lib.get("libName", "").strip()
            # 이름에 '영어' 가 들어간 도서관만 채택 (오탐 방지)
            if code and "영어" in libname:
                found[code] = libname
        time.sleep(REQUEST_DELAY)

    result = list(found.items())
    print(f"    영어 도서관 {len(result)}곳 확인:")
    for code, libname in result:
        print(f"      - {libname} ({code})")
    return result


# ----------------------------------------------------------------------------
# 1단계(B): 도서관 지정 인기대출 수집  (권장)
# ----------------------------------------------------------------------------
def fetch_loans_by_library():
    """영어 특화 도서관별로 loanItemSrchByLib 를 돌며 인기대출을 수집,
    ISBN 접두어로 영어원서만 남기고 대출횟수를 합산한다.
    """
    libraries = resolve_library_codes()
    if not libraries:
        print("[!] 대상 도서관을 찾지 못했습니다. TARGET_LIB_CODES 를 직접 지정하세요.")
        return {}

    books = {}  # isbn13 -> record
    for code, libname in libraries:
        print(f"[수집] {libname or code} 인기대출...")
        for page in range(1, MAX_PAGES + 1):
            data = call_api("loanItemSrchByLib", {
                "libCode": code,
                "pageNo": page,
                "pageSize": PAGE_SIZE,
            })
            if not data:
                break
            docs = data.get("response", {}).get("docs", [])
            if not docs:
                break

            new_in_page = 0
            for item in docs:
                doc = item.get("doc", {})
                isbn13 = (doc.get("isbn13") or "").replace("-", "").strip()
                if not is_english_original(isbn13):
                    continue
                try:
                    loan_count = int(doc.get("loan_count", 0) or 0)
                except ValueError:
                    loan_count = 0

                if isbn13 in books:
                    books[isbn13]["loan_count"] += loan_count
                    books[isbn13]["libraries"].add(libname or code)
                else:
                    books[isbn13] = {
                        "isbn13": isbn13,
                        "bookname": doc.get("bookname", "").strip(),
                        "authors": doc.get("authors", "").strip(),
                        "publisher": doc.get("publisher", "").strip(),
                        "publication_year": doc.get("publication_year", "").strip(),
                        "class_no": doc.get("class_no", "").strip(),
                        "vol": doc.get("vol", "").strip(),
                        "loan_count": loan_count,
                        "libraries": {libname or code},
                        "age_ranges": set(),
                    }
                    new_in_page += 1
            print(f"    p{page}: 영어원서 {new_in_page}건 신규 (누적 {len(books)}건)")
            time.sleep(REQUEST_DELAY)

    return books


# ----------------------------------------------------------------------------
# 1단계(A): 전국통합 인기대출 수집  (영어원서 비중 매우 낮음 - 참고용)
# ----------------------------------------------------------------------------
def fetch_popular_loans():
    """연령대별로 loanItemSrch 를 돌며 인기대출도서를 수집.
    반환: {isbn13: {bookname, authors, publisher, publication_year,
                    isbn13, class_no, loan_count(합산), vol}}
    """
    books = {}  # isbn13 -> record

    for from_age, to_age in AGE_RANGES:
        print(f"[수집] 연령 {from_age}~{to_age}세 인기대출도서...")
        for page in range(1, MAX_PAGES + 1):
            data = call_api("loanItemSrch", {
                "from_age": from_age,
                "to_age": to_age,
                "pageNo": page,
                "pageSize": PAGE_SIZE,
            })
            if not data:
                break

            docs = data.get("response", {}).get("docs", [])
            if not docs:
                break

            new_in_page = 0
            for item in docs:
                doc = item.get("doc", {})
                isbn13 = (doc.get("isbn13") or "").replace("-", "").strip()
                if not is_english_original(isbn13):
                    continue

                try:
                    loan_count = int(doc.get("loan_count", 0) or 0)
                except ValueError:
                    loan_count = 0

                if isbn13 in books:
                    # 여러 연령대에 걸쳐 나타나면 대출횟수 합산
                    books[isbn13]["loan_count"] += loan_count
                    books[isbn13]["age_ranges"].add(f"{from_age}-{to_age}")
                else:
                    books[isbn13] = {
                        "isbn13": isbn13,
                        "bookname": doc.get("bookname", "").strip(),
                        "authors": doc.get("authors", "").strip(),
                        "publisher": doc.get("publisher", "").strip(),
                        "publication_year": doc.get("publication_year", "").strip(),
                        "class_no": doc.get("class_no", "").strip(),
                        "vol": doc.get("vol", "").strip(),
                        "loan_count": loan_count,
                        "age_ranges": {f"{from_age}-{to_age}"},
                    }
                    new_in_page += 1

            print(f"    p{page}: 영어원서 {new_in_page}건 신규 (누적 {len(books)}건)")
            time.sleep(REQUEST_DELAY)

    return books


# ----------------------------------------------------------------------------
# 2단계: 도서 상세정보 결합 (표지/저자/소개)
# ----------------------------------------------------------------------------
def enrich_details(records):
    """상위 도서에 srchDtlList 로 표지 URL, 책소개 등을 붙인다."""
    print(f"[상세] 상위 {len(records)}권 상세정보 조회...")
    for i, rec in enumerate(records, 1):
        data = call_api("srchDtlList", {
            "isbn13": rec["isbn13"],
            "loaninfoYN": "N",
        })
        if data:
            detail = data.get("response", {}).get("detail", [])
            if detail:
                book = detail[0].get("book", {})
                rec["bookImageURL"] = book.get("bookImageURL", "").strip()
                rec["description"] = book.get("description", "").strip()
                rec["class_nm"] = book.get("class_nm", "").strip()
                if not rec.get("authors"):
                    rec["authors"] = book.get("authors", "").strip()
        if i % 10 == 0:
            print(f"    {i}/{len(records)} 완료")
        time.sleep(REQUEST_DELAY)
    return records


# ----------------------------------------------------------------------------
# 3단계: 저장
# ----------------------------------------------------------------------------
def save_outputs(records):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # set 필드를 정렬된 문자열로 변환
    for rec in records:
        if isinstance(rec.get("age_ranges"), set):
            rec["age_ranges"] = ", ".join(sorted(rec["age_ranges"]))
        if isinstance(rec.get("libraries"), set):
            rec["libraries"] = ", ".join(sorted(rec["libraries"]))

    json_path = os.path.join(OUTPUT_DIR, "english_books_curated.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    csv_path = os.path.join(OUTPUT_DIR, "english_books_curated.csv")
    fields = ["rank", "bookname", "authors", "publisher", "publication_year",
              "isbn13", "loan_count", "libraries", "age_ranges", "class_no",
              "class_nm", "bookImageURL", "description"]
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for rank, rec in enumerate(records, 1):
            rec["rank"] = rank
            writer.writerow(rec)

    print(f"\n[완료] 총 {len(records)}권 저장")
    print(f"  - JSON: {json_path}")
    print(f"  - CSV : {csv_path}  (엑셀에서 바로 열림, UTF-8 BOM)")


# ----------------------------------------------------------------------------
# 메인
# ----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="유아·초등 영어원서 큐레이션")
    parser.add_argument("--top", type=int, default=TOP_N,
                        help=f"상세조회할 상위 권수 (기본 {TOP_N})")
    parser.add_argument("--no-detail", action="store_true",
                        help="상세정보(표지/소개) 조회 건너뛰기")
    parser.add_argument("--mode", choices=["library", "national"], default="library",
                        help="library=영어도서관 지정 수집(권장), national=전국통합(참고용)")
    args = parser.parse_args()

    print("=" * 60)
    print(" 조이네영어도서관 - 유아·초등 영어원서 큐레이션")
    print("=" * 60)

    # 1) 수집 + 필터
    if args.mode == "library":
        books = fetch_loans_by_library()
    else:
        books = fetch_popular_loans()
    if not books:
        print("\n[중단] 수집된 영어원서가 없습니다. "
              "인증키 활성화 상태 또는 호출 제한을 확인하세요.")
        return

    # 2) 대출횟수 기준 정렬
    records = sorted(books.values(), key=lambda r: r["loan_count"], reverse=True)
    print(f"\n[정렬] 영어원서 총 {len(records)}종 (대출횟수 순)")

    # 3) 상위 N권만 상세조회
    top_records = records[:args.top]
    if not args.no_detail:
        top_records = enrich_details(top_records)

    # 4) 저장
    save_outputs(top_records)


if __name__ == "__main__":
    main()

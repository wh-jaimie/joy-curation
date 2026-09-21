# -*- coding: utf-8 -*-
"""953 영어원서 -> 시리즈 분류 + OpenLibrary 표지/책소개 결합 -> enriched.json"""
import csv, os, re, json, time, sys, urllib.request, urllib.error

CSV_PATH = r"C:\Users\user1\Downloads\BestLoanList_20260921103300\20260921103300\인기대출도서_2026.csv"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
OUT_JSON = os.path.join(OUT_DIR, "enriched.json")
UA = "ChoiEnglishLibrary/1.0 (curation; contact jabbaek@gmail.com)"
ENRICH_TOP = 100          # 책소개 붙일 상위 권수(대출순)
DELAY = 0.35

# 시리즈 분류 규칙: (표시명, 소문자 매칭 패턴들). 위에서부터 먼저 매칭.
SERIES_RULES = [
    ("Oxford Reading Tree", ["oxford reading tree", "ort ", "read with biff"]),
    ("Dog Man", ["dog man"]),
    ("Cat Kid Comic Club", ["cat kid"]),
    ("Captain Underpants", ["captain underpants"]),
    ("Dragon Masters", ["dragon masters"]),
    ("Press Start! (Super Rabbit Boy)", ["super rabbit boy", "press start", "robo-rabbit"]),
    ("Pizza and Taco", ["pizza and taco"]),
    ("Diary of a Wimpy Kid", ["wimpy kid", "diary of a wimpy"]),
    ("Fly Guy", ["fly guy"]),
    ("Biscuit", ["biscuit"]),
    ("Elephant & Piggie", ["elephant & piggie", "elephant and piggie", "piggie", "an elephant"]),
    ("Pete the Cat", ["pete the cat"]),
    ("Fancy Nancy", ["fancy nancy"]),
    ("Peppa Pig", ["peppa pig", "peppa"]),
    ("Berenstain Bears", ["berenstain"]),
    ("National Geographic Readers", ["national geographic"]),
    ("The Bad Guys", ["the bad guys", "bad guys"]),
    ("Creepy (Aaron Reynolds)", ["creepy carrots", "creepy pair", "creepy crayon", "creepy"]),
    ("Little Critter", ["little critter"]),
    ("Curious George", ["curious george"]),
    ("Splat the Cat", ["splat the cat"]),
    ("Frog and Toad", ["frog and toad"]),
    ("Clifford", ["clifford"]),
    ("Skippyjon Jones", ["skippyjon"]),
    ("Winnie and Wilbur", ["winnie and wilbur", "winnie the witch"]),
    ("Maisy", ["maisy"]),
]

def classify(title):
    t = title.lower()
    for name, pats in SERIES_RULES:
        if any(p in t for p in pats):
            return name
    return None

def load():
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        lines = f.readlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("순위"))
    rows = list(csv.reader(lines[start:]))
    h = [x.strip() for x in rows[0]]
    ii = {n: h.index(n) for n in ["서명","저자","출판사","출판년도","ISBN","KDC","대출건수"]}
    out = []
    for r in rows[1:]:
        if len(r) < 8 or not r[0].strip():
            continue
        isbn = r[ii["ISBN"]].replace("-", "").strip()
        if isbn[:4] not in ("9780", "9781"):
            continue
        try: loans = int(r[ii["대출건수"]] or 0)
        except ValueError: loans = 0
        out.append({
            "title": r[ii["서명"]].strip(),
            "author": r[ii["저자"]].strip(),
            "publisher": r[ii["출판사"]].strip(),
            "year": r[ii["출판년도"]].strip(),
            "isbn": isbn,
            "loans": loans,
            "series": classify(r[ii["서명"]].strip()),
            "cover": f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg",
            "desc": "",
        })
    out.sort(key=lambda d: d["loans"], reverse=True)
    for rank, d in enumerate(out, 1):
        d["rank"] = rank
    return out

def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))

def fetch_desc(isbn):
    """edition -> works 폴백으로 책소개 확보."""
    try:
        ed = _get(f"https://openlibrary.org/isbn/{isbn}.json")
    except Exception:
        return ""
    def norm(d):
        if isinstance(d, str): return d
        if isinstance(d, dict): return d.get("value", "")
        return ""
    desc = norm(ed.get("description"))
    if not desc and ed.get("works"):
        try:
            wk = _get(f"https://openlibrary.org{ed['works'][0]['key']}.json")
            desc = norm(wk.get("description"))
        except Exception:
            pass
    # 각주/마크다운 꼬리 정리
    desc = re.split(r"\(\[source", desc)[0].strip()
    return desc

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    books = load()
    print(f"영어원서 {len(books)}종 로드")
    print(f"상위 {ENRICH_TOP}종 책소개 조회(OpenLibrary)...")
    got = 0
    for i, b in enumerate(books[:ENRICH_TOP], 1):
        b["desc"] = fetch_desc(b["isbn"])
        if b["desc"]: got += 1
        if i % 20 == 0:
            print(f"  {i}/{ENRICH_TOP} (소개 확보 {got})")
        time.sleep(DELAY)
    print(f"책소개 확보: {got}/{ENRICH_TOP}")
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=1)
    print(f"저장: {OUT_JSON}")

    # 시리즈 통계
    from collections import Counter
    sc = Counter(b["series"] for b in books if b["series"])
    print("\n=== 시리즈 종수 TOP 15 ===")
    for s, n in sc.most_common(15):
        print(f"{n:4}  {s}")
    print(f"시리즈 미분류(단행본 등): {sum(1 for b in books if not b['series'])}종")

if __name__ == "__main__":
    main()

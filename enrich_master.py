# -*- coding: utf-8 -*-
"""파닉스 전 엄마표영어 그림책 마스터 리스트 -> OpenLibrary 표지/ISBN + 도서관 대출 교차 -> master.json"""
import csv, os, re, json, time, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = r"C:\Users\user1\Downloads\BestLoanList_20260921103300\20260921103300\인기대출도서_2026.csv"
OUT = os.path.join(HERE, "output", "master.json")
UA = "ChoiEnglishLibrary/1.0 (curation; contact jabbaek@gmail.com)"
DELAY = 0.3

# ── 파닉스 전 단계별 마스터 리스트 ─────────────────────────────────────────
# stage: 0=보드북/사물인지, 1=노래·챈트, 2=반복패턴 첫그림책, 3=이야기 그림책(파닉스 직전)
STAGES = {
    0: {"label": "1단계 · 보드북 & 사물인지", "age": "0~24개월",
        "desc": "만지고 넘기며 사물·색·동물 이름을 귀로 익히는 첫 책. 문장이 거의 없어 엄마가 부담 없이 시작."},
    1: {"label": "2단계 · 노래 & 챈트(마더구스)", "age": "12개월~4세",
        "desc": "멜로디에 얹혀 저절로 따라부르게 되는 노래책. 세이펜/음원과 함께 들려주기 좋음."},
    2: {"label": "3단계 · 반복 패턴 첫 그림책", "age": "2~5세",
        "desc": "같은 문장이 반복돼 아이가 다음 쪽을 예측하며 '읽는 척'하게 되는 책. 읽어주기 입문."},
    3: {"label": "4단계 · 이야기 그림책(파닉스 직전)", "age": "3~6세",
        "desc": "줄거리가 있는 명작 그림책. 파닉스 시작 전 듣기 그릇을 키우는 단계."},
}

MASTER = [
    # ── 1단계 보드북/사물인지 ──
    ("Dear Zoo", "Rod Campbell", 0, "플랩을 열면 동물이 나오는 국민 첫 책. 동물·형용사 반복."),
    ("Where's Spot?", "Eric Hill", 0, "플랩 놀이로 'Is he ...?' 전치사·장소를 자연스럽게."),
    ("Brown Bear, Brown Bear, What Do You See?", "Bill Martin Jr., Eric Carle", 0, "색+동물+반복 질문. 파닉스 전 최고의 입문서."),
    ("Color Zoo", "Lois Ehlert", 0, "도형과 색을 오려낸 보드북. 노부영 베이비 베스트 수록."),
    ("Ten Little Fingers and Ten Little Toes", "Mem Fox", 0, "리듬감 있는 아기 신체 노래책."),
    ("Where Is Baby's Belly Button?", "Karen Katz", 0, "플랩으로 신체 부위 익히기. 돌 전후 최고 인기."),
    ("That's Not My Teddy", "Fiona Watt", 0, "촉감 보드북. 'It's too ...' 형용사 반복."),
    ("Global Babies", "Global Fund for Children", 0, "세계 아기 사진책. 아주 어린 아기 시선 맞추기 좋음."),

    # ── 2단계 노래·챈트 ──
    ("The Wheels on the Bus", "Annie Kubler", 1, "마더구스 대표곡. 손유희와 함께."),
    ("Five Little Monkeys Jumping on the Bed", "Eileen Christelow", 1, "숫자 세기+반복 노래. 아이들이 열광."),
    ("The Itsy Bitsy Spider", "Annie Kubler", 1, "손유희 마더구스 클래식."),
    ("Walking Through the Jungle", "Debbie Harter (Barefoot)", 1, "동물+소리 반복 챈트. Barefoot Sing-along."),
    ("Row, Row, Row Your Boat", "Annie Kubler", 1, "짧고 쉬운 첫 노래책."),
    ("Hush Little Baby", "Sylvia Long", 1, "자장가 그림책. 노부영 베이비 베스트 수록."),
    ("Head, Shoulders, Knees and Toes", "Annie Kubler", 1, "몸을 움직이며 부르는 액션송."),
    ("If You're Happy and You Know It", "Jane Cabrera", 1, "감정+동작 액션송."),

    # ── 3단계 반복 패턴 첫 그림책 ──
    ("The Very Hungry Caterpillar", "Eric Carle", 2, "요일·숫자·먹이 반복. 파닉스 전 필독 1순위."),
    ("We're Going on a Bear Hunt", "Michael Rosen, Helen Oxenbury", 2, "소리말 반복 챈트. 온몸으로 읽는 책."),
    ("From Head to Toe", "Eric Carle", 2, "동물 동작 따라하기. 'Can you do it?' 반복."),
    ("Does a Kangaroo Have a Mother, Too?", "Eric Carle", 2, "동물 엄마-아기 반복 질문. 노부영 수록."),
    ("Goodnight Moon", "Margaret Wise Brown", 2, "잠자리 반복 그림책. 노부영 베이비 베스트 수록."),
    ("Time for Bed", "Mem Fox", 2, "운율 있는 잠자리 책. 부드러운 라임."),
    ("Polar Bear, Polar Bear, What Do You Hear?", "Bill Martin Jr., Eric Carle", 2, "Brown Bear 후속. 동물 소리 반복."),
    ("Ten in the Bed", "Penny Dale", 2, "숫자 거꾸로 세기 반복 노래책."),
    ("The Very Busy Spider", "Eric Carle", 2, "촉감+반복 문장. 동물 소리 누적."),
    ("Handa's Surprise", "Eileen Browne", 2, "과일·동물 반복. 그림으로 유추하는 재미."),

    # ── 4단계 이야기 그림책(파닉스 직전) ──
    ("Pete the Cat: I Love My White Shoes", "Eric Litwin, James Dean", 3, "노래+반복 후렴. 긍정 메시지."),
    ("Llama Llama Red Pajama", "Anna Dewdney", 3, "라임 있는 잠자리 이야기. 분리불안 공감."),
    ("Where the Wild Things Are", "Maurice Sendak", 3, "상상력 명작. 감정 다루기."),
    ("The Gruffalo", "Julia Donaldson, Axel Scheffler", 3, "라임 스토리텔링 최고봉. 반복 대사."),
    ("Room on the Broom", "Julia Donaldson, Axel Scheffler", 3, "운율 있는 마녀 이야기. 협동 주제."),
    ("Press Here", "Hervé Tullet", 3, "상호작용 그림책. 지시문 따라 놀기."),
    ("Chicka Chicka Boom Boom", "Bill Martin Jr., John Archambault", 3, "알파벳 챈트. 파닉스 다리 놓기."),
    ("Dr. Seuss's ABC", "Dr. Seuss", 3, "라임으로 익히는 알파벳. 파닉스 직전."),
    ("The Napping House", "Audrey Wood, Don Wood", 3, "누적 반복 구조. 잠자리 유머."),
    ("Maisy Goes to the Library", "Lucy Cousins", 3, "생활 밀착 캐릭터. 쉬운 일상 문장."),
    ("Caps for Sale", "Esphyr Slobodkina", 3, "반복 대사 명작. 원숭이 흉내."),
    ("If You Give a Mouse a Cookie", "Laura Numeroff", 3, "순환 구조 이야기. 인과 반복."),
]

def norm(t):
    t = t.lower()
    t = re.split(r"[:(]", t)[0]
    t = re.sub(r"[^a-z0-9 ]", "", t)
    return re.sub(r"\s+", " ", t).strip()

# 도서관 대출 CSV 로드 (영어원서만)
def load_loans():
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        lines = f.readlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("순위"))
    rows = list(csv.reader(lines[start:]))
    h = [x.strip() for x in rows[0]]
    ti, ii, li, ri = h.index("서명"), h.index("ISBN"), h.index("대출건수"), h.index("순위")
    loans = []
    for r in rows[1:]:
        if len(r) < 8 or not r[0].strip():
            continue
        isbn = r[ii].replace("-", "").strip()
        if isbn[:4] not in ("9780", "9781"):
            continue
        try: lc = int(r[li] or 0)
        except ValueError: lc = 0
        loans.append({"title": r[ti].strip(), "norm": norm(r[ti]), "loans": lc, "rank": int(r[ri])})
    return loans

def match_loan(title, loans):
    n = norm(title)
    best = None
    for x in loans:
        if n and (n in x["norm"] or x["norm"] in n) and abs(len(n) - len(x["norm"])) < 25:
            if best is None or x["loans"] > best["loans"]:
                best = x
    return best

def ol_search(title, author):
    q = urllib.parse.urlencode({"title": title, "author": author.split(",")[0], "limit": 1,
                                "fields": "title,author_name,first_publish_year,isbn,cover_i,cover_edition_key"})
    url = f"https://openlibrary.org/search.json?{q}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.loads(r.read().decode("utf-8"))
        docs = d.get("docs") or []
        if not docs:
            return {}
        doc = docs[0]
        isbn = (doc.get("isbn") or [""])[0]
        cover = None
        if doc.get("cover_i"):
            cover = f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-L.jpg"
        elif isbn:
            cover = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
        return {"isbn": isbn, "cover": cover, "year": doc.get("first_publish_year", "")}
    except Exception as e:
        print("  ol err:", title, e)
        return {}

def main():
    loans = load_loans()
    print(f"도서관 영어원서 {len(loans)}종 로드")
    out = []
    for i, (title, author, stage, reason) in enumerate(MASTER, 1):
        ol = ol_search(title, author)
        lm = match_loan(title, loans)
        out.append({
            "title": title, "author": author, "stage": stage, "reason": reason,
            "isbn": ol.get("isbn", ""), "cover": ol.get("cover"), "year": ol.get("year", ""),
            "lib_loans": lm["loans"] if lm else 0,
            "lib_rank": lm["rank"] if lm else 0,
        })
        cov = "표지O" if ol.get("cover") else "표지X"
        lib = f"대출{lm['loans']}회(#{lm['rank']})" if lm else "도서관없음"
        print(f"  {i:2}/{len(MASTER)} {title[:32]:32} {cov} {lib}")
        time.sleep(DELAY)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"stages": STAGES, "books": out}, f, ensure_ascii=False, indent=1)
    got = sum(1 for b in out if b["cover"])
    inlib = sum(1 for b in out if b["lib_loans"] > 0)
    print(f"\n마스터 {len(out)}종 | 표지 {got}종 | 도서관 대출 확인 {inlib}종 -> {OUT}")

if __name__ == "__main__":
    main()

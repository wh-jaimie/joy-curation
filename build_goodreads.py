# -*- coding: utf-8 -*-
"""Goodreads 3개 셸프(인기순) 합산 -> 파닉스 전 그림책 큐레이션 + OpenLibrary 표지 -> gr_master.json"""
import os, re, json, time, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = r"C:\Users\user1\Downloads\BestLoanList_20260921103300\20260921103300\인기대출도서_2026.csv"
OUT = os.path.join(HERE, "output", "gr_master.json")
UA = "ChoiEnglishLibrary/1.0 (curation; contact jabbaek@gmail.com)"
DELAY = 0.3

# 각 셸프의 인기순 목록 (Goodreads 셸프 노출 순서 = 전세계 담김 수 순서)
PICTURE = [
"Where the Wild Things Are|Maurice Sendak","The Very Hungry Caterpillar|Eric Carle","The Giving Tree|Shel Silverstein",
"Green Eggs and Ham|Dr. Seuss","Goodnight Moon|Margaret Wise Brown","If You Give a Mouse a Cookie|Laura Numeroff",
"The Day the Crayons Quit|Drew Daywalt","Don't Let the Pigeon Drive the Bus!|Mo Willems","The Cat in the Hat|Dr. Seuss",
"I Want My Hat Back|Jon Klassen","The True Story of the 3 Little Pigs|Jon Scieszka","The Snowy Day|Ezra Jack Keats",
"Oh, the Places You'll Go!|Dr. Seuss","Corduroy|Don Freeman","This Is Not My Hat|Jon Klassen",
"The Polar Express|Chris Van Allsburg","Madeline|Ludwig Bemelmans","Brown Bear, Brown Bear, What Do You See?|Bill Martin Jr.",
"Chicka Chicka Boom Boom|Bill Martin Jr.","The Lorax|Dr. Seuss","How the Grinch Stole Christmas!|Dr. Seuss",
"Alexander and the Terrible, Horrible, No Good, Very Bad Day|Judith Viorst","Click, Clack, Moo: Cows That Type|Doreen Cronin",
"Last Stop on Market Street|Matt de la Peña","Knuffle Bunny|Mo Willems","The Rainbow Fish|Marcus Pfister",
"Love You Forever|Robert Munsch","Cloudy with a Chance of Meatballs|Judi Barrett","The Adventures of Beekle|Dan Santat",
"Harold and the Purple Crayon|Crockett Johnson","Make Way for Ducklings|Robert McCloskey","Extra Yarn|Mac Barnett",
"Stellaluna|Janell Cannon","The Mitten|Jan Brett","One Fish, Two Fish, Red Fish, Blue Fish|Dr. Seuss",
"Blueberries for Sal|Robert McCloskey","Dragons Love Tacos|Adam Rubin","The Paper Bag Princess|Robert Munsch",
"The Story of Ferdinand|Munro Leaf","Are You My Mother?|P.D. Eastman","Flotsam|David Wiesner","Strega Nona|Tomie dePaola",
"Caps for Sale|Esphyr Slobodkina","The Monster at the End of this Book|Jon Stone","Kitten's First Full Moon|Kevin Henkes",
"The Book with No Pictures|B.J. Novak","Sam & Dave Dig a Hole|Mac Barnett","A Sick Day for Amos McGee|Philip C. Stead",
"Chrysanthemum|Kevin Henkes","Olivia|Ian Falconer",
]
BOARD = [
"Moo, Baa, La La La!|Sandra Boynton","The Very Hungry Caterpillar|Eric Carle","Brown Bear, Brown Bear, What Do You See?|Bill Martin Jr.",
"Goodnight Moon|Margaret Wise Brown","The Going To Bed Book|Sandra Boynton","Barnyard Dance|Sandra Boynton",
"Guess How Much I Love You|Sam McBratney","Blue Hat, Green Hat|Sandra Boynton","Dear Zoo|Rod Campbell",
"Little Blue Truck|Alice Schertle","But Not the Hippopotamus|Sandra Boynton","Doggies|Sandra Boynton",
"Where Is Baby's Belly Button?|Karen Katz","Snuggle Puppy!|Sandra Boynton","Good Night, Gorilla|Peggy Rathmann",
"Peek-a-Who?|Nina Laden","Belly Button Book|Sandra Boynton","Pajama Time!|Sandra Boynton",
"Chicka Chicka Boom Boom|Bill Martin Jr.","The Runaway Bunny|Margaret Wise Brown","We're Going on a Bear Hunt|Michael Rosen",
"Opposites|Sandra Boynton","Mr. Brown Can Moo! Can You?|Dr. Seuss","Dr. Seuss's ABC|Dr. Seuss","Dinosaur Dance!|Sandra Boynton",
"Where's Spot?|Eric Hill","Giraffes Can't Dance|Giles Andreae","Polar Bear, Polar Bear, What Do You Hear?|Bill Martin Jr.",
"I Love You Through and Through|Bernadette Rossetti-Shustak","Big Red Barn|Margaret Wise Brown","Hand, Hand, Fingers, Thumb|Al Perkins",
"Yummy Yucky|Leslie Patricelli","Are You My Mother?|P.D. Eastman","I Am a Bunny|Ole Risom",
"Five Little Monkeys Jumping on the Bed|Eileen Christelow","Time for Bed|Mem Fox","Global Babies|The Global Fund for Children",
"On the Night You Were Born|Nancy Tillman","Jamberry|Bruce Degen","Giraffes Can't Dance|Giles Andreae",
]
TODDLER = [
"The Very Hungry Caterpillar|Eric Carle","Brown Bear, Brown Bear, What Do You See?|Bill Martin Jr.","Goodnight Moon|Margaret Wise Brown",
"Dear Zoo|Rod Campbell","From Head to Toe|Eric Carle","Good Night, Gorilla|Peggy Rathmann","Where Is the Green Sheep?|Mem Fox",
"Chicka Chicka Boom Boom|Bill Martin Jr.","Moo, Baa, La La La!|Sandra Boynton","Freight Train|Donald Crews",
"We're Going on a Bear Hunt|Michael Rosen","Ten Little Fingers and Ten Little Toes|Mem Fox","Little Blue Truck|Alice Schertle",
"Guess How Much I Love You|Sam McBratney","Barnyard Dance|Sandra Boynton","The Going To Bed Book|Sandra Boynton",
"Llama Llama Red Pajama|Anna Dewdney","Hooray for Fish|Lucy Cousins","Time for Bed|Mem Fox","Bark, George|Jules Feiffer",
"Jamberry|Bruce Degen","Don't Let the Pigeon Drive the Bus!|Mo Willems","Clip-Clop|Nicola Smee","The Very Busy Spider|Eric Carle",
"Goodnight, Goodnight, Construction Site|Sherri Duskey Rinker","I'm the Biggest Thing in the Ocean!|Kevin Sherry",
"Polar Bear, Polar Bear, What Do You Hear?|Bill Martin Jr.","Corduroy|Don Freeman","Pete the Cat: I Love My White Shoes|Eric Litwin",
"Big Red Barn|Margaret Wise Brown","Where the Wild Things Are|Maurice Sendak","I Went Walking|Sue Williams",
"A Parade of Elephants|Kevin Henkes","Can You Make a Scary Face?|Jan Thomas","Owl Babies|Martin Waddell",
"The Runaway Bunny|Margaret Wise Brown","Are You My Mother?|P.D. Eastman","Where's Spot?|Eric Hill","Press Here|Hervé Tullet",
"The Snowy Day|Ezra Jack Keats","The Little Mouse, the Red Ripe Strawberry, and the Big Hungry Bear|Don Wood",
"Belly Button Book|Sandra Boynton","But Not the Hippopotamus|Sandra Boynton","Hooray for Birds!|Lucy Cousins",
"Peek-a-Moo!|Marie Torres Cimarusti","The Monster at the End of this Book|Jon Stone","The Cat in the Hat|Dr. Seuss",
"Spunky Little Monkey|Bill Martin Jr.","Jump!|Scott M. Fischer","If You Give a Mouse a Cookie|Laura Numeroff",
]

def norm(t):
    t = t.lower(); t = re.split(r"[:(]", t)[0]
    t = t.replace("&", "and"); t = re.sub(r"[^a-z0-9 ]", "", t)
    return re.sub(r"\s+", " ", t).strip()

# 합산: 위치가 앞일수록 점수↑, 어린 셸프(board/toddler) 가중
books = {}
def add(shelf_list, tag, weight):
    n = len(shelf_list)
    for pos, entry in enumerate(shelf_list):
        title, author = entry.split("|")
        k = norm(title)
        b = books.setdefault(k, {"title": title, "author": author, "score": 0.0, "shelves": set(), "best": {}})
        b["score"] += (n - pos) * weight
        b["shelves"].add(tag)
        b["best"][tag] = pos + 1
        if len(title) > len(b["title"]):  # 더 완전한 제목 채택
            b["title"] = title

add(PICTURE, "그림책", 1.0)
add(BOARD, "보드북", 1.35)
add(TODDLER, "토들러", 1.35)

merged = list(books.values())
merged.sort(key=lambda b: b["score"], reverse=True)

# 연령대(가장 어린 셸프 기준)
def band(sh):
    if "보드북" in sh: return ("A", "아기·첫책 (0~2세)")
    if "토들러" in sh: return ("B", "유아 (2~4세)")
    return ("C", "미취학 (4~6세)")

# 도서관 대출 엄격 매칭
def load_loans():
    import csv
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        lines = f.readlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("순위"))
    rows = list(__import__("csv").reader(lines[start:]))
    h = [x.strip() for x in rows[0]]
    ti, ii, li = h.index("서명"), h.index("ISBN"), h.index("대출건수")
    m = {}
    for r in rows[1:]:
        if len(r) < 8 or not r[0].strip(): continue
        isbn = r[ii].replace("-", "").strip()
        if isbn[:4] not in ("9780", "9781"): continue
        try: lc = int(r[li] or 0)
        except ValueError: lc = 0
        nk = norm(r[ti])
        if nk and (nk not in m or lc > m[nk]):
            m[nk] = lc
    return m
loans = load_loans()

def ol(title, author):
    q = urllib.parse.urlencode({"title": title, "author": author.split(",")[0], "limit": 1,
        "fields": "isbn,cover_i,first_publish_year"})
    try:
        req = urllib.request.Request(f"https://openlibrary.org/search.json?{q}", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.loads(r.read().decode("utf-8"))
        doc = (d.get("docs") or [{}])[0]
        cover = f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-L.jpg" if doc.get("cover_i") else \
                (f"https://covers.openlibrary.org/b/isbn/{doc['isbn'][0]}-L.jpg" if doc.get("isbn") else None)
        return cover, doc.get("first_publish_year", "")
    except Exception:
        return None, ""

out = []
for rank, b in enumerate(merged, 1):
    bd = band(b["shelves"])
    cover, year = ol(b["title"], b["author"])
    lib = loans.get(norm(b["title"]), 0)
    out.append({
        "rank": rank, "title": b["title"], "author": b["author"],
        "band_key": bd[0], "band": bd[1],
        "shelves": sorted(b["shelves"]), "score": round(b["score"], 1),
        "cover": cover, "year": year, "lib_loans": lib,
    })
    print(f"{rank:3} [{bd[0]}] {b['title'][:38]:38} {'표지O' if cover else '표지X'} {'대출'+str(lib) if lib else ''}")
    time.sleep(DELAY)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"books": out}, f, ensure_ascii=False, indent=1)
print(f"\n총 {len(out)}종 | 표지 {sum(1 for b in out if b['cover'])} | 도서관대출확인 {sum(1 for b in out if b['lib_loans'])} -> {OUT}")
from collections import Counter
print("연령대 분포:", dict(Counter(b["band"] for b in out)))

# -*- coding: utf-8 -*-
"""파닉스 전 120권 챌린지 커리큘럼 (24주제 × 5권 난이도 계단) + OpenLibrary 표지/검증 -> challenge.json"""
import os, json, time, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output", "challenge.json")
UA = "ChoiEnglishLibrary/1.0 (curation; contact jabbaek@gmail.com)"
DELAY = 0.25

TIER_LABELS = {
    1: "아주 쉬운 반복",
    2: "그림 중심",
    3: "이야기 시작",
    4: "유머·재미",
    5: "조금 긴 책",
}

# 각 주제: (emoji, 영문명, 한글명, [ (tier, title, author, reason) × 5 ])
CURRICULUM = [
("🐻","Animals","동물",[
 (1,"Brown Bear, Brown Bear, What Do You See?","Bill Martin Jr.","색+동물+반복 질문의 정석"),
 (2,"Dear Zoo","Rod Campbell","플랩 열면 동물, 형용사 반복"),
 (3,"Polar Bear, Polar Bear, What Do You Hear?","Bill Martin Jr.","동물 소리로 확장"),
 (4,"Moo, Baa, La La La!","Sandra Boynton","동물 소리 흉내로 깔깔"),
 (5,"From Head to Toe","Eric Carle","동작 따라하는 참여형"),
]),
("🚗","Vehicles","탈것",[
 (1,"Freight Train","Donald Crews","색+기차, 아주 단순"),
 (2,"Little Blue Truck","Alice Schertle","\"Beep!\" 의성어 반복"),
 (3,"Goodnight, Goodnight, Construction Site","Sherri Duskey Rinker","공사장 차 재우는 이야기"),
 (4,"Don't Let the Pigeon Drive the Bus!","Mo Willems","\"No!\" 외치는 유머"),
 (5,"Sheep in a Jeep","Nancy Shaw","라임 가득한 소동극"),
]),
("🍎","Food","음식",[
 (1,"Yummy Yucky","Leslie Patricelli","먹는 것/못 먹는 것 대비"),
 (2,"Jamberry","Bruce Degen","베리 말놀이 라임"),
 (3,"The Very Hungry Caterpillar","Eric Carle","요일·음식 반복, 필독"),
 (4,"Dragons Love Tacos","Adam Rubin","타코 좋아하는 용의 유머"),
 (5,"Cloudy with a Chance of Meatballs","Judi Barrett","음식이 내리는 상상 이야기"),
]),
("🌈","Colors","색깔",[
 (1,"Blue Hat, Green Hat","Sandra Boynton","\"Oops!\" 색+유머 반복"),
 (2,"Mouse Paint","Ellen Stoll Walsh","색이 섞이는 놀이"),
 (3,"Little Blue and Little Yellow","Leo Lionni","색으로 그린 우정 이야기"),
 (4,"A Color of His Own","Leo Lionni","색을 못 정하는 카멜레온"),
 (5,"The Day the Crayons Quit","Drew Daywalt","크레용들의 편지, 조금 긺"),
]),
("🔢","Numbers","숫자",[
 (1,"Doggies","Sandra Boynton","강아지 세기+소리"),
 (2,"Ten Black Dots","Donald Crews","점으로 배우는 숫자"),
 (3,"Five Little Monkeys Jumping on the Bed","Eileen Christelow","숫자 노래 이야기"),
 (4,"Chicka Chicka 1, 2, 3","Bill Martin Jr.","숫자 챈트의 유머판"),
 (5,"Ten Apples Up on Top!","Dr. Seuss","라임으로 세는 소동"),
]),
("👨‍👩‍👧","Family","가족",[
 (1,"I Love You Through and Through","Bernadette Rossetti-Shustak","온몸으로 사랑 표현"),
 (2,"Guess How Much I Love You","Sam McBratney","사랑을 크기로 비교"),
 (3,"The Runaway Bunny","Margaret Wise Brown","\"늘 찾아갈게\" 대화체"),
 (4,"Are You My Mother?","P.D. Eastman","엄마 찾기 반복+유머"),
 (5,"Love You Forever","Robert Munsch","대를 잇는 사랑, 뭉클"),
]),
("🌙","Bedtime","잠자리",[
 (1,"The Going to Bed Book","Sandra Boynton","잘 준비 순서 라임"),
 (2,"Goodnight Moon","Margaret Wise Brown","\"굿나잇\" 반복의 정석"),
 (3,"Time for Bed","Mem Fox","동물 엄마의 자장 라임"),
 (4,"Llama Llama Red Pajama","Anna Dewdney","잠자리 분리불안 공감"),
 (5,"How Do Dinosaurs Say Good Night?","Jane Yolen","공룡의 잠투정, 조금 긺"),
]),
("😊","Feelings","감정",[
 (1,"The Feelings Book","Todd Parr","감정 어휘 아주 단순하게"),
 (2,"Glad Monster, Sad Monster","Ed Emberley","가면으로 감정 놀이"),
 (3,"The Color Monster","Anna Llenas","감정을 색으로 정리"),
 (4,"When Sophie Gets Angry—Really, Really Angry","Molly Bang","화를 다루는 이야기"),
 (5,"In My Heart: A Book of Feelings","Jo Witek","마음을 들여다보기"),
]),
("👣","Body","몸",[
 (1,"Where Is Baby's Belly Button?","Karen Katz","플랩으로 신체 찾기"),
 (2,"Head, Shoulders, Knees and Toes","Annie Kubler","몸 움직이는 액션송"),
 (3,"Here Are My Hands","Bill Martin Jr.","신체 부위 라임"),
 (4,"Belly Button Book","Sandra Boynton","배꼽 노래 유머"),
 (5,"Ten Little Fingers and Ten Little Toes","Mem Fox","세계 아기 손발 라임"),
]),
("🐛","Bugs","곤충",[
 (1,"The Very Busy Spider","Eric Carle","촉감+반복 문장"),
 (2,"In the Tall, Tall Grass","Denise Fleming","풀숲 소리 라임"),
 (3,"The Grouchy Ladybug","Eric Carle","시간+무당벌레 이야기"),
 (4,"There Was an Old Lady Who Swallowed a Fly","Pam Adams","누적 반복 유머"),
 (5,"Some Bugs","Angela DiTerlizzi","온갖 곤충 라임 탐험"),
]),
("🦖","Dinosaurs","공룡",[
 (1,"Dinosaur Roar!","Paul Stickland","공룡+반대말 아주 단순"),
 (2,"Dinosaur Dance!","Sandra Boynton","공룡 춤 챈트"),
 (3,"How Do Dinosaurs Eat Their Food?","Jane Yolen","식사 예절 이야기"),
 (4,"Dinosaur vs. Bedtime","Bob Shea","공룡 대 잠자리, 유머"),
 (5,"Tyrannosaurus Drip","Julia Donaldson","라임 서사, 조금 긺"),
]),
("🌱","Nature","자연·정원",[
 (1,"Planting a Rainbow","Lois Ehlert","색+꽃 심기 단순"),
 (2,"The Carrot Seed","Ruth Krauss","믿음의 씨앗, 짧은 명작"),
 (3,"The Tiny Seed","Eric Carle","씨앗의 한 해 이야기"),
 (4,"Lola Plants a Garden","Anna McQuinn","정원 가꾸는 일상"),
 (5,"Miss Rumphius","Barbara Cooney","세상을 아름답게, 긴 명작"),
]),
("🌦️","Weather & Seasons","날씨·계절",[
 (1,"Rain","Robert Kalan","색+비, 아주 단순"),
 (2,"Little Cloud","Eric Carle","구름이 변신하는 상상"),
 (3,"The Snowy Day","Ezra Jack Keats","눈 오는 날의 하루"),
 (4,"The Mitten","Jan Brett","장갑에 모이는 동물들"),
 (5,"Tap the Magic Tree","Christie Matheson","사계절 나무 상호작용"),
]),
("🐶","Pets","반려동물",[
 (1,"Where's Spot?","Eric Hill","플랩으로 강아지 찾기"),
 (2,"Biscuit","Alyssa Satin Capucilli","가장 쉬운 강아지 리더"),
 (3,"Harry the Dirty Dog","Gene Zion","목욕 싫은 강아지 이야기"),
 (4,"Bark, George","Jules Feiffer","엉뚱한 소리+반전 유머"),
 (5,"Clifford the Big Red Dog","Norman Bridwell","큰 강아지의 하루, 조금 긺"),
]),
("🚜","Farm","농장",[
 (1,"Big Red Barn","Margaret Wise Brown","농장의 하루 라임"),
 (2,"Barnyard Dance","Sandra Boynton","흥나는 농장 챈트"),
 (3,"Mrs. Wishy-Washy","Joy Cowley","반복되는 농장 소동"),
 (4,"Click, Clack, Moo: Cows That Type","Doreen Cronin","타자 치는 소들 유머"),
 (5,"The Little Red Hen","Paul Galdone","도와줄래? 누적 이야기"),
]),
("🌊","Ocean","바다",[
 (1,"Hooray for Fish!","Lucy Cousins","온갖 물고기+사랑"),
 (2,"Commotion in the Ocean","Giles Andreae","바다 동물 라임"),
 (3,"The Rainbow Fish","Marcus Pfister","비늘을 나누는 이야기"),
 (4,"I'm the Biggest Thing in the Ocean!","Kevin Sherry","허세+반전 유머"),
 (5,"Swimmy","Leo Lionni","함께의 힘, 명작"),
]),
("👻","Monsters","괴물",[
 (1,"Go Away, Big Green Monster!","Ed Emberley","페이지로 괴물 없애기"),
 (2,"The Monster at the End of This Book","Jon Stone","넘기지 말라는 참여형"),
 (3,"Where the Wild Things Are","Maurice Sendak","상상 놀이 명작"),
 (4,"Leonardo the Terrible Monster","Mo Willems","안 무서운 괴물 유머"),
 (5,"The Gruffalo","Julia Donaldson","라임 서사의 최고봉"),
]),
("🎃","Halloween","할로윈",[
 (1,"Where Is Baby's Pumpkin?","Karen Katz","플랩 할로윈 찾기"),
 (2,"Five Little Pumpkins","Public Domain","호박 다섯 라임"),
 (3,"Room on the Broom","Julia Donaldson","마녀 빗자루 라임 이야기"),
 (4,"Creepy Carrots!","Aaron Reynolds","오싹+웃긴 당근"),
 (5,"The Little Old Lady Who Was Not Afraid of Anything","Linda Williams","누적 반복, 조금 긺"),
]),
("🎄","Christmas","크리스마스",[
 (1,"Dear Santa","Rod Campbell","플랩 산타 선물"),
 (2,"Llama Llama Holiday Drama","Anna Dewdney","기다림의 라임"),
 (3,"The Night Before Christmas","Clement C. Moore","고전 크리스마스 시"),
 (4,"How the Grinch Stole Christmas!","Dr. Seuss","그린치의 라임 이야기"),
 (5,"The Polar Express","Chris Van Allsburg","기차 여행 명작, 긺"),
]),
("🎶","Songs & Rhymes","노래·마더구스",[
 (1,"The Wheels on the Bus","Annie Kubler","손유희 대표곡"),
 (2,"The Itsy Bitsy Spider","Annie Kubler","손유희 클래식"),
 (3,"If You're Happy and You Know It","Jane Cabrera","감정+동작 액션송"),
 (4,"Down by the Bay","Raffi","말장난 라임 노래"),
 (5,"Over in the Meadow","Public Domain","숫자 세는 자연 노래"),
]),
("🏫","School & Friends","학교·친구",[
 (1,"Maisy Goes to Preschool","Lucy Cousins","쉬운 유치원 일상"),
 (2,"The Kissing Hand","Audrey Penn","등원 불안 달래기"),
 (3,"How Do Dinosaurs Go to School?","Jane Yolen","학교 예절 유머"),
 (4,"We Don't Eat Our Classmates","Ryan T. Higgins","친구 사귀기 유머"),
 (5,"Chrysanthemum","Kevin Henkes","이름과 자존감, 긺"),
]),
("🛁","Daily Routine","생활습관",[
 (1,"Potty","Leslie Patricelli","배변 훈련 입문"),
 (2,"Pajama Time!","Sandra Boynton","잘 준비 챈트"),
 (3,"Bathtime for Biscuit","Alyssa Satin Capucilli","목욕 시간 강아지"),
 (4,"How Do Dinosaurs Clean Their Rooms?","Jane Yolen","정리 예절 유머"),
 (5,"The Napping House","Audrey Wood","누적 반복, 조금 긺"),
]),
("🔀","Opposites & Concepts","반대말·개념",[
 (1,"Opposites","Sandra Boynton","반대말 보드북"),
 (2,"Round Is a Mooncake","Roseanne Thong","도형을 일상에서"),
 (3,"Mouse Shapes","Ellen Stoll Walsh","도형으로 만드는 놀이"),
 (4,"Duck! Rabbit!","Amy Krouse Rosenthal","관점 바꾸는 유머"),
 (5,"Press Here","Hervé Tullet","상호작용의 끝판왕"),
]),
("🎨","Imagination","상상·놀이",[
 (1,"Not a Box","Antoinette Portis","상자로 상상하기"),
 (2,"Harold and the Purple Crayon","Crockett Johnson","크레용으로 그린 세상"),
 (3,"The Adventures of Beekle","Dan Santat","상상 친구 찾기"),
 (4,"Sam & Dave Dig a Hole","Mac Barnett","구멍 파기+그림 반전"),
 (5,"Journey","Aaron Becker","글 없는 상상 여행, 긺"),
]),
]

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
        return cover, (doc.get("isbn") or [""])[0], doc.get("first_publish_year", "")
    except Exception:
        return None, "", ""

def slugify(s):
    import re
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

themes = []
misses = []
gid = 0
for emoji, en, ko, books in CURRICULUM:
    tb = []
    for tier, title, author, reason in books:
        gid += 1
        cover, isbn, year = ol(title, author)
        if not cover:
            misses.append(f"{ko}/{title}")
        tb.append({
            "gid": gid, "tier": tier, "tier_label": TIER_LABELS[tier],
            "title": title, "author": author, "reason": reason,
            "cover": cover, "isbn": isbn, "year": year,
            "id": "c" + str(gid),
        })
        time.sleep(DELAY)
    themes.append({"emoji": emoji, "en": en, "ko": ko, "key": slugify(en), "books": tb})
    print(f"  {emoji} {ko} ({en}) — 표지 {sum(1 for b in tb if b['cover'])}/5")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump({"themes": themes, "tier_labels": TIER_LABELS, "total": gid}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n총 {gid}권 · 주제 {len(themes)}개 -> {OUT}")
print(f"표지 미확보 {len(misses)}권:")
for m in misses:
    print("  -", m)

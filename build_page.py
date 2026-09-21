# -*- coding: utf-8 -*-
"""enriched.json -> 큐레이션 웹페이지(index.html) 생성. 데이터는 HTML에 embed."""
import json, os, re, html
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "output", "enriched.json")
OUT = os.path.join(HERE, "output", "index.html")

def clean_author(a):
    if not a:
        return ""
    a = re.sub(r"\((지은이|글|그림|옮긴이|by)\)", "", a)
    a = re.sub(r"\b(words|pictures|story|art|illustrated by|written by|by)\b[:,]?", "", a, flags=re.I)
    a = a.split(";")[0]
    a = re.sub(r"\s+", " ", a).strip(" ,.;:")
    return a

with open(DATA, encoding="utf-8") as f:
    books = json.load(f)

for b in books:
    b["author"] = clean_author(b.get("author", ""))
    d = (b.get("desc") or "").strip().strip('"').strip()
    d = re.sub(r"--+$", "", d).strip()
    if len(d) < 15:  # 너무 짧은 조각 제거
        d = ""
    b["desc"] = d

books.sort(key=lambda x: x["loans"], reverse=True)

# 시리즈 집계
series_agg = defaultdict(lambda: {"count": 0, "loans": 0, "books": []})
for b in books:
    s = b["series"] or "__single__"
    series_agg[s]["count"] += 1
    series_agg[s]["loans"] += b["loans"]
    series_agg[s]["books"].append(b)

# 표시할 시리즈(단행본 제외), 대출합 순
series_list = sorted(
    [(k, v) for k, v in series_agg.items() if k != "__single__"],
    key=lambda kv: kv[1]["loans"], reverse=True,
)
series_cards = []
for name, v in series_list:
    top = sorted(v["books"], key=lambda x: x["loans"], reverse=True)[:6]
    series_cards.append({
        "name": name, "count": v["count"], "loans": v["loans"],
        "covers": [{"isbn": t["isbn"], "title": t["title"]} for t in top],
    })

total_books = len(books)
total_loans = sum(b["loans"] for b in books)
n_series = len(series_list)
n_single = series_agg["__single__"]["count"]

payload = {
    "books": books,
    "series": series_cards,
    "stats": {
        "total_books": total_books, "total_loans": total_loans,
        "n_series": n_series, "n_single": n_single,
    },
    "series_names": [c["name"] for c in series_cards],
}

TEMPLATE = r"""<title>조이네 영어원서 책장</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Nunito+Sans:wght@400;600;700;800&display=swap');

:root{
  --ground:#F5F1E8; --surface:#FFFDF8; --surface-2:#EFE9DB;
  --ink:#2B2A26; --ink-soft:#6C665A; --line:#E1D9C8;
  --teal:#0E7C7B; --teal-deep:#0A5E5D; --coral:#E8623C; --amber:#E9A63B;
  --shadow:0 1px 2px rgba(43,42,38,.06),0 6px 18px rgba(43,42,38,.07);
  --shadow-lg:0 10px 34px rgba(43,42,38,.14);
}
:root:not([data-theme="light"]){ }
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#1B1A17; --surface:#242220; --surface-2:#2E2B27;
    --ink:#F1ECE1; --ink-soft:#A8A090; --line:#3A362F;
    --teal:#3FB0AE; --teal-deep:#5CC6C4; --coral:#F27E5B; --amber:#F0B857;
    --shadow:0 1px 2px rgba(0,0,0,.3),0 6px 18px rgba(0,0,0,.4);
    --shadow-lg:0 12px 38px rgba(0,0,0,.55);
  }
}
:root[data-theme="dark"]{
  --ground:#1B1A17; --surface:#242220; --surface-2:#2E2B27;
  --ink:#F1ECE1; --ink-soft:#A8A090; --line:#3A362F;
  --teal:#3FB0AE; --teal-deep:#5CC6C4; --coral:#F27E5B; --amber:#F0B857;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 6px 18px rgba(0,0,0,.4);
  --shadow-lg:0 12px 38px rgba(0,0,0,.55);
}

*{box-sizing:border-box}
body{background:var(--ground);color:var(--ink);
  font-family:'Nunito Sans',system-ui,-apple-system,'Segoe UI',sans-serif;
  line-height:1.55;-webkit-font-smoothing:antialiased}
.wrap{max-width:1120px;margin:0 auto;padding-inline:20px}
h1,h2,h3{font-family:'Fraunces',Georgia,serif;font-weight:600;line-height:1.12;
  text-wrap:balance;margin:0}
.tnum{font-variant-numeric:tabular-nums}
a{color:inherit}

/* header */
header.top{position:sticky;top:env(safe-area-inset-top,0px);z-index:50;
  background:color-mix(in srgb,var(--ground) 88%,transparent);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.top .wrap{display:flex;align-items:center;gap:14px;padding-block:12px}
.brand{display:flex;align-items:center;gap:10px;font-family:'Fraunces',serif;
  font-weight:700;font-size:1.05rem;letter-spacing:.2px;white-space:nowrap}
.brand .mark{width:30px;height:30px;border-radius:9px;flex:0 0 auto;
  background:linear-gradient(135deg,var(--teal),var(--teal-deep));
  display:grid;place-items:center;color:#fff;font-size:1rem;box-shadow:var(--shadow)}
.top .search{margin-left:auto;position:relative;flex:1;max-width:340px}
.top .search input{width:100%;padding:9px 12px 9px 34px;border-radius:999px;
  border:1px solid var(--line);background:var(--surface);color:var(--ink);
  font:inherit;font-size:.9rem}
.top .search svg{position:absolute;left:11px;top:50%;transform:translateY(-50%);
  width:16px;height:16px;color:var(--ink-soft)}
.themebtn{border:1px solid var(--line);background:var(--surface);color:var(--ink);
  width:38px;height:38px;border-radius:10px;cursor:pointer;font-size:1rem;flex:0 0 auto}

/* hero */
.hero{padding-block:44px 30px}
.eyebrow{font-size:.78rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;
  color:var(--teal-deep)}
.hero h1{font-size:clamp(2rem,5.5vw,3.3rem);margin:.35em 0 .3em;font-weight:700}
.hero p.lead{font-size:1.06rem;color:var(--ink-soft);max-width:60ch}
.stats{display:flex;flex-wrap:wrap;gap:12px;margin-top:26px}
.stat{background:var(--surface);border:1px solid var(--line);border-radius:14px;
  padding:14px 18px;box-shadow:var(--shadow);min-width:130px}
.stat .n{font-family:'Fraunces',serif;font-weight:700;font-size:1.7rem;
  color:var(--teal-deep)}
.stat .l{font-size:.82rem;color:var(--ink-soft);margin-top:2px}
.note{font-size:.8rem;color:var(--ink-soft);margin-top:14px}

/* section */
section{padding-block:30px}
.sec-head{display:flex;align-items:baseline;justify-content:space-between;gap:12px;
  margin-bottom:18px;flex-wrap:wrap}
.sec-head h2{font-size:clamp(1.45rem,3.5vw,2rem)}
.sec-head .sub{color:var(--ink-soft);font-size:.9rem}

/* top20 shelf */
.shelf{display:grid;grid-template-columns:repeat(auto-fill,minmax(158px,1fr));gap:18px}
.bookcard{background:var(--surface);border:1px solid var(--line);border-radius:14px;
  overflow:hidden;box-shadow:var(--shadow);display:flex;flex-direction:column;
  transition:transform .16s ease,box-shadow .16s ease}
.bookcard:hover{transform:translateY(-3px);box-shadow:var(--shadow-lg)}
.cover{position:relative;aspect-ratio:3/4;background:var(--surface-2);overflow:hidden}
.cover img{width:100%;height:100%;object-fit:cover;display:block}
.cover .ph{position:absolute;inset:0;display:none;flex-direction:column;
  justify-content:center;padding:14px;text-align:center;
  background:linear-gradient(150deg,var(--teal),var(--teal-deep));color:#fff}
.cover .ph .pt{font-family:'Fraunces',serif;font-weight:600;font-size:.92rem;line-height:1.2}
.cover.noimg .ph{display:flex}
.rankbadge{position:absolute;top:8px;left:8px;background:var(--coral);color:#fff;
  font-weight:800;font-size:.78rem;padding:3px 8px;border-radius:8px;box-shadow:var(--shadow)}
.loanbadge{position:absolute;bottom:8px;right:8px;
  background:color-mix(in srgb,var(--ink) 82%,transparent);color:#fff;
  font-weight:700;font-size:.72rem;padding:3px 7px;border-radius:7px}
.bookcard .body{padding:11px 12px 13px;display:flex;flex-direction:column;gap:3px;flex:1}
.bookcard .t{font-family:'Fraunces',serif;font-weight:600;font-size:.98rem;line-height:1.2}
.bookcard .a{font-size:.79rem;color:var(--ink-soft)}
.bookcard .stag{margin-top:auto;font-size:.7rem;font-weight:700;color:var(--teal-deep);
  letter-spacing:.02em;padding-top:6px}
.bookcard .d{font-size:.8rem;color:var(--ink-soft);margin-top:5px;
  display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}

/* series */
.series-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px}
.scard{background:var(--surface);border:1px solid var(--line);border-radius:16px;
  padding:16px;box-shadow:var(--shadow);cursor:pointer;transition:transform .16s,box-shadow .16s}
.scard:hover{transform:translateY(-2px);box-shadow:var(--shadow-lg)}
.scard h3{font-size:1.12rem}
.scard .meta{font-size:.82rem;color:var(--ink-soft);margin-top:3px}
.scard .strip{display:flex;gap:6px;margin-top:12px}
.scard .strip .mini{aspect-ratio:3/4;width:100%;border-radius:6px;overflow:hidden;
  background:var(--surface-2);position:relative}
.scard .strip .mini img{width:100%;height:100%;object-fit:cover}
.scard .strip .mini .mph{position:absolute;inset:0;display:none;place-items:center;
  background:linear-gradient(150deg,var(--teal),var(--teal-deep))}
.scard .strip .mini.noimg .mph{display:grid}

/* filters + full list */
.filters{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px}
.chip{border:1px solid var(--line);background:var(--surface);color:var(--ink-soft);
  padding:6px 13px;border-radius:999px;font:inherit;font-size:.82rem;font-weight:700;
  cursor:pointer;white-space:nowrap}
.chip.active{background:var(--teal-deep);color:#fff;border-color:var(--teal-deep)}
.toolbar{display:flex;align-items:center;gap:10px;margin:14px 0 18px;flex-wrap:wrap}
.toolbar select{padding:7px 11px;border-radius:9px;border:1px solid var(--line);
  background:var(--surface);color:var(--ink);font:inherit;font-size:.85rem}
.count{font-size:.85rem;color:var(--ink-soft);margin-left:auto}
.list{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}
.row{display:flex;gap:12px;background:var(--surface);border:1px solid var(--line);
  border-radius:12px;padding:10px;box-shadow:var(--shadow);align-items:center}
.row .rc{width:46px;flex:0 0 auto;aspect-ratio:3/4;border-radius:6px;overflow:hidden;
  background:var(--surface-2);position:relative}
.row .rc img{width:100%;height:100%;object-fit:cover}
.row .rc .rph{position:absolute;inset:0;display:none;place-items:center;font-size:.9rem;
  background:linear-gradient(150deg,var(--teal),var(--teal-deep));color:#fff}
.row .rc.noimg .rph{display:grid}
.row .info{min-width:0;flex:1}
.row .info .t{font-family:'Fraunces',serif;font-weight:600;font-size:.92rem;line-height:1.2;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.row .info .a{font-size:.76rem;color:var(--ink-soft);overflow:hidden;text-overflow:ellipsis;
  white-space:nowrap}
.row .info .m{font-size:.72rem;color:var(--teal-deep);font-weight:700;margin-top:2px}
.row .rk{font-family:'Fraunces',serif;font-weight:700;color:var(--ink-soft);font-size:.85rem;
  flex:0 0 auto}
.more{display:block;margin:22px auto 0;padding:11px 22px;border-radius:999px;
  border:1px solid var(--line);background:var(--surface);color:var(--ink);font:inherit;
  font-weight:700;cursor:pointer;box-shadow:var(--shadow)}
footer{border-top:1px solid var(--line);margin-top:30px;padding-block:26px 40px}
footer p{color:var(--ink-soft);font-size:.82rem;margin:.3em 0}
@media (max-width:560px){
  .top .brand span.full{display:none}
  .shelf{grid-template-columns:repeat(auto-fill,minmax(132px,1fr));gap:12px}
}
</style>

<header class="top"><div class="wrap">
  <div class="brand"><span class="mark">책</span><span class="full">조이네 영어원서 책장</span></div>
  <div class="search">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4-4"/></svg>
    <input id="q" type="search" placeholder="제목·저자·시리즈 검색" autocomplete="off">
  </div>
  <button class="themebtn" id="theme" title="테마 전환">◐</button>
</div></header>

<main class="wrap">
  <section class="hero">
    <div class="eyebrow">도서관 정보나루 · 전국 공공도서관 대출 데이터</div>
    <h1>2026년, 아이들이 가장 많이 빌린 영어원서</h1>
    <p class="lead">국립중앙도서관 도서관 정보나루의 영유아·유아(0~7세) 국외도서 대출 데이터에서
      영어원서만 골라, 실제 <strong>대출 건수</strong> 순으로 정리한 큐레이션입니다.</p>
    <div class="stats" id="stats"></div>
    <p class="note">※ 집계 기간 2026-01-01 ~ 2026-09-20 · 대상 연령 0~7세 · 영어원서 판별 기준 ISBN 978-0/978-1(영어권 출판)</p>
  </section>

  <section>
    <div class="sec-head"><h2>대출 TOP 20</h2><span class="sub">이 연령대 대출을 휩쓴 인기 원서</span></div>
    <div class="shelf" id="top20"></div>
  </section>

  <section>
    <div class="sec-head"><h2>시리즈 컬렉션</h2><span class="sub">권수가 많은 인기 시리즈 — 카드를 누르면 전체 목록에서 필터됩니다</span></div>
    <div class="series-grid" id="series"></div>
  </section>

  <section>
    <div class="sec-head"><h2>전체 목록</h2><span class="sub" id="allsub"></span></div>
    <div class="filters" id="chips"></div>
    <div class="toolbar">
      <label>정렬
        <select id="sort">
          <option value="loans">대출 많은 순</option>
          <option value="rank">인기 순위 순</option>
          <option value="title">제목 순</option>
        </select>
      </label>
      <span class="count" id="count"></span>
    </div>
    <div class="list" id="list"></div>
    <button class="more" id="more" hidden>더 보기</button>
  </section>
</main>

<footer><div class="wrap">
  <p><strong>조이네 영어원서 책장</strong> — 큐레이션 데이터</p>
  <p>출처: 국립중앙도서관 도서관 정보나루(data4library.kr) 인기대출도서 · 표지: Open Library</p>
  <p>이용허락: 저작자표시(BY)</p>
</div></footer>

<script>
const PAYLOAD = /*DATA*/;
const {books, series, stats, series_names} = PAYLOAD;
const esc = s => (s||"").replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const covL = isbn => `https://covers.openlibrary.org/b/isbn/${isbn}-L.jpg?default=false`;
const covM = isbn => `https://covers.openlibrary.org/b/isbn/${isbn}-M.jpg?default=false`;
const fmt = n => n.toLocaleString('en-US');

// stats
document.getElementById('stats').innerHTML = [
  [fmt(stats.total_books), '영어원서 종수'],
  [fmt(stats.total_loans), '총 대출 건수'],
  [fmt(stats.n_series)+'+', '인기 시리즈'],
  ['449', 'Oxford Reading Tree'],
].map(([n,l])=>`<div class="stat"><div class="n tnum">${n}</div><div class="l">${l}</div></div>`).join('');

// helper: 이미지 로드 실패시 placeholder
function imgFallback(el){ el.parentElement.classList.add('noimg'); el.remove(); }
window._imgErr = imgFallback;

// TOP 20
document.getElementById('top20').innerHTML = books.slice(0,20).map(b=>`
  <article class="bookcard">
    <div class="cover">
      <img loading="lazy" src="${covL(b.isbn)}" alt="${esc(b.title)}" onerror="_imgErr(this)">
      <div class="ph"><div class="pt">${esc(b.title)}</div></div>
      <span class="rankbadge">#${b.rank}</span>
      <span class="loanbadge tnum">${fmt(b.loans)}회</span>
    </div>
    <div class="body">
      <div class="t">${esc(b.title)}</div>
      <div class="a">${esc(b.author)||'&nbsp;'}</div>
      ${b.desc?`<div class="d">${esc(b.desc)}</div>`:''}
      ${b.series?`<div class="stag">${esc(b.series)}</div>`:''}
    </div>
  </article>`).join('');

// SERIES cards
document.getElementById('series').innerHTML = series.slice(0,12).map(s=>`
  <div class="scard" data-series="${esc(s.name)}">
    <h3>${esc(s.name)}</h3>
    <div class="meta tnum">${s.count}종 · 대출 ${fmt(s.loans)}회</div>
    <div class="strip">${s.covers.map(c=>`
      <div class="mini"><img loading="lazy" src="${covM(c.isbn)}" alt="" onerror="_imgErr(this)"><div class="mph"></div></div>`).join('')}</div>
  </div>`).join('');
document.querySelectorAll('.scard').forEach(el=>el.addEventListener('click',()=>{
  setSeries(el.dataset.series);
  document.getElementById('chips').scrollIntoView({behavior:'smooth',block:'start'});
}));

// FULL LIST with filter/sort/search
let curSeries='__all__', curSort='loans', curQ='', shown=60;
const chipsEl=document.getElementById('chips');
const chipDefs=[['__all__','전체'],...series_names.slice(0,10).map(n=>[n,n]),['__single__','단행본·기타']];
chipsEl.innerHTML=chipDefs.map(([v,l])=>`<button class="chip${v==='__all__'?' active':''}" data-v="${esc(v)}">${esc(l)}</button>`).join('');
chipsEl.querySelectorAll('.chip').forEach(c=>c.addEventListener('click',()=>setSeries(c.dataset.v)));
function setSeries(v){curSeries=v;shown=60;
  chipsEl.querySelectorAll('.chip').forEach(c=>c.classList.toggle('active',c.dataset.v===v));render();}
document.getElementById('sort').addEventListener('change',e=>{curSort=e.target.value;render();});
document.getElementById('q').addEventListener('input',e=>{curQ=e.target.value.toLowerCase().trim();shown=60;render();});
document.getElementById('more').addEventListener('click',()=>{shown+=60;render();});

function filtered(){
  let r=books.filter(b=>{
    if(curSeries==='__single__'){if(b.series)return false;}
    else if(curSeries!=='__all__'){if(b.series!==curSeries)return false;}
    if(curQ){const hay=(b.title+' '+b.author+' '+(b.series||'')).toLowerCase();if(!hay.includes(curQ))return false;}
    return true;
  });
  if(curSort==='title')r.sort((a,b)=>a.title.localeCompare(b.title));
  else if(curSort==='rank')r.sort((a,b)=>a.rank-b.rank);
  else r.sort((a,b)=>b.loans-a.loans);
  return r;
}
function render(){
  const r=filtered();
  document.getElementById('count').textContent=`${fmt(r.length)}종`;
  document.getElementById('list').innerHTML=r.slice(0,shown).map(b=>`
    <div class="row">
      <div class="rc"><img loading="lazy" src="${covM(b.isbn)}" alt="" onerror="_imgErr(this)"><div class="rph">📖</div></div>
      <div class="info">
        <div class="t">${esc(b.title)}</div>
        <div class="a">${esc(b.author)||'&nbsp;'}</div>
        <div class="m tnum">대출 ${fmt(b.loans)}회${b.series?' · '+esc(b.series):''}</div>
      </div>
      <div class="rk tnum">#${b.rank}</div>
    </div>`).join('');
  document.getElementById('more').hidden = r.length<=shown;
}
document.getElementById('allsub').textContent=`영어원서 ${fmt(stats.total_books)}종 전체를 검색·필터·정렬`;
render();

// theme toggle
const root=document.documentElement;
try{const t=localStorage.getItem('joy-theme');if(t)root.setAttribute('data-theme',t);}catch(e){}
document.getElementById('theme').addEventListener('click',()=>{
  const cur=root.getAttribute('data-theme');
  const dark=cur?cur==='dark':matchMedia('(prefers-color-scheme:dark)').matches;
  const next=dark?'light':'dark';root.setAttribute('data-theme',next);
  try{localStorage.setItem('joy-theme',next);}catch(e){}
});
</script>
"""

html_out = TEMPLATE.replace("/*DATA*/", json.dumps(payload, ensure_ascii=False))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html_out)
print(f"생성: {OUT}  ({len(html_out)//1024} KB)")
print(f"책 {total_books}종, 시리즈 {n_series}개, 단행본 {n_single}종")

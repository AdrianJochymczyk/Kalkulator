# -*- coding: utf-8 -*-
"""Generuje samodzielny raport HTML (research/raport_spolki_it_polska.html) z danych w build.py.
Uruchomienie: python3 research/build_html.py  (najpierw build.py, aby istniały wykresy)
"""
import base64
import html
import os
import re

from build import COMPANIES, HERE, NIE, margin, rj

E = html.escape


def img(name):
    with open(os.path.join(HERE, "charts", name), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def num(v):
    if v is None:
        return f'<span class="na">{NIE}</span>'
    return f"{v:,.0f}".replace(",", "&nbsp;")


def pct(c):
    m = margin(c)
    return f"{m:.1f}%".replace(".", ",") if m is not None else f'<span class="na">{NIE}</span>'


def linkify(text):
    out, last = [], 0
    for m in re.finditer(r"https?://[^\s,)]+", text):
        out.append(E(text[last:m.start()]))
        u = m.group(0).rstrip(".;")
        out.append(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(short_url(u))}</a>')
        last = m.start() + len(u)
    out.append(E(text[last:]))
    return "".join(out)


def short_url(u):
    u = re.sub(r"^https?://(www\.)?", "", u)
    return u if len(u) <= 60 else u[:57] + "…"


LEVEL = {"rdzeń": ("rdzeń", "lvl-core"), "oferta dedykowana": ("dedykowana oferta", "lvl-ded"),
         "pośredni": ("pośredni", "lvl-ind"), "marginalny": ("marginalny", "lvl-low"), "brak": ("brak", "lvl-none")}


def badge(c):
    t, cls = LEVEL[c["poziom_bud"]]
    return f'<span class="badge {cls}">{t}</span>'


def src_badge(c):
    if c["zrodlo_fin"] == "pierwotne":
        return '<span class="src src-ok" title="Dane odczytane z raportu rocznego / ESPI / ESEF">raport</span>'
    return '<span class="src src-agg" title="Dane z agregatora sprawozdań KRS – wymagają weryfikacji w RDF">agregator*</span>'


def table_rows():
    rows = []
    for i, c in enumerate(sorted(COMPANIES, key=lambda c: c["przychody"], reverse=True), 1):
        m = margin(c)
        rows.append(f"""<tr>
<td class="r">{i}</td><td><strong>{E(c['nazwa'].split(' (')[0])}</strong></td>
<td class="mono"><a href="{rj(c['krs'])}" target="_blank" rel="noopener">{c['krs']}</a></td>
<td>{E(c['kategoria'])}</td><td>{E(c['produkt'])}</td><td>{badge(c)}</td>
<td>{E(c['rok'])}</td>
<td class="r" data-v="{c['przychody']}">{num(c['przychody'])}</td>
<td class="r" data-v="{c['zysk_netto'] if c['zysk_netto'] is not None else ''}">{num(c['zysk_netto'])}</td>
<td class="r" data-v="{'' if m is None else round(m, 2)}">{pct(c)}</td>
<td>{src_badge(c)}</td>
<td><a href="{E(c['link_raportu'])}" target="_blank" rel="noopener">link</a></td></tr>""")
    return "\n".join(rows)


def cards():
    groups = [("A. Spółki giełdowe – dane z raportów rocznych", lambda c: c["zrodlo_fin"] == "pierwotne" or c["nazwa"].startswith("Comarch")),
              ("B. Prywatni dostawcy i wdrożeniowcy ERP – dane z agregatorów KRS",
               lambda c: c["zrodlo_fin"] == "agregator" and c["poziom_bud"] != "rdzeń" and not c["nazwa"].startswith("Comarch")),
              ("C. Oprogramowanie i dane dla budownictwa – dane z agregatorów KRS", lambda c: c["poziom_bud"] == "rdzeń")]
    out, n = [], 0
    for title, f in groups:
        out.append(f'<h3 class="grp">{E(title)}</h3><div class="cards">')
        for c in [c for c in COMPANIES if f(c)]:
            n += 1
            fin = [("Przychody", c["przychody"]), ("Zysk brutto ze sprzedaży", c["zysk_brutto_sprz"]),
                   ("EBIT", c["ebit"]), ("EBITDA", c["ebitda"]), ("Zysk netto", c["zysk_netto"])]
            fin_html = "".join(f"<div><dt>{k}</dt><dd>{num(v)}</dd></div>" for k, v in fin)
            pdf = (f'<a href="{E(c["plik"])}">{E(os.path.basename(c["plik"]))}</a>' if c["plik"]
                   else '<span class="na">brak pliku PDF (sprawozdanie dostępne tylko w RDF/KRS)</span>')
            out.append(f"""<article class="card" id="s{n}">
<header><h4>{n}. {E(c['nazwa'])}</h4>{badge(c)}</header>
<p class="ids">KRS <a href="{rj(c['krs'])}" target="_blank" rel="noopener" class="mono">{c['krs']}</a> · NIP <span class="mono">{E(c['nip'])}</span> · REGON <span class="mono">{E(c['regon'])}</span></p>
<p class="meta">{E(c['siedziba'])} · <a href="{E(c['www'])}" target="_blank" rel="noopener">{E(short_url(c['www']))}</a></p>
<p class="cat">{E(c['kategoria'])}</p>
<p>{E(c['opis'])}</p>
<p class="bud"><strong>Budownictwo:</strong> {linkify(c['budownictwo'])}</p>
<div class="fin"><p class="finhead">Rok {E(c['rok'])} · tys. {E(c['waluta'])} · {E(c['typ'])} {src_badge(c)}</p>
<dl>{fin_html}<div><dt>Marża netto</dt><dd>{pct(c)}</dd></div></dl>
{f'<p class="small">EBITDA: {E(c["ebitda_uwagi"])}</p>' if c['ebitda_uwagi'] else ''}
<p class="small">Data publikacji: {E(c['data_pub'])} · Raport: <a href="{E(c['link_raportu'])}" target="_blank" rel="noopener">{E(short_url(c['link_raportu']))}</a> · Plik: {pdf}</p></div>
<details><summary>Uwagi i źródła</summary><p class="small">{linkify(c['uwagi'])}</p></details>
</article>""")
        out.append("</div>")
    return "\n".join(out)


def kpis():
    prim = [c for c in COMPANIES if c["zrodlo_fin"] == "pierwotne"]
    core = [c for c in COMPANIES if c["poziom_bud"] == "rdzeń"]
    core_rev = sum(c["przychody"] for c in core) / 1000
    return f"""<div class="kpis">
<div class="kpi"><span class="kv">{len(COMPANIES)}</span><span class="kl">spółek w zestawieniu</span></div>
<div class="kpi"><span class="kv">{len(prim)}</span><span class="kl">z danymi z raportów rocznych</span></div>
<div class="kpi"><span class="kv">{len(core)}</span><span class="kl">z budownictwem jako rdzeniem działalności</span></div>
<div class="kpi"><span class="kv">≈{core_rev:.0f} mln zł</span><span class="kl">łączne przychody firm „budowlanych”</span></div>
</div>"""


REPORTS = [
    ("Asseco_Poland_2025_jednostkowe_sprawozdanie_finansowe.pdf", "Asseco Poland – jednostkowe SF 2025 (render ESEF)"),
    ("Asseco_Business_Solutions_2025_jednostkowe_sprawozdanie_finansowe.pdf", "Asseco BS – jednostkowe SF 2025 (render ESEF)"),
    ("Asseco_Business_Solutions_2025_prezentacja_wynikow.pdf", "Asseco BS – prezentacja wyników 2025"),
    ("Comarch_2025_raport_roczny.pdf", "Comarch – raport roczny 2025 (dane Grupy)"),
    ("Sygnity_2025_jednostkowe_sprawozdanie_finansowe.pdf", "Sygnity – jednostkowe SF 2025 (render ESEF)"),
    ("Vercom_2025_jednostkowe_sprawozdanie_finansowe.pdf", "Vercom – jednostkowe SF 2025 (render ESEF)"),
    ("Vercom_2025_sprawozdanie_zarzadu.pdf", "Vercom – sprawozdanie zarządu / raport Grupy 2025"),
    ("Shoper_2025_jednostkowe_sprawozdanie_finansowe.pdf", "Shoper – jednostkowe SF 2025 (render ESEF)"),
    ("Text_2025-26_sprawozdanie_zarzadu.pdf", "Text – sprawozdanie zarządu FY2025/26 (render ESEF)"),
    ("iFirma_2025_sprawozdanie_finansowe.pdf", "iFirma – SF 2025 (render ESEF)"),
]

CSS = """
:root{--bg:#f6f5f2;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#7a7974;--line:#e4e3df;--accent:#2a78d6;--accent2:#eb6834;
--core-bg:#dff3e9;--core-fg:#0b6b46;--ded-bg:#dce9fa;--ded-fg:#1c5cab;--ind-bg:#fdf0d5;--ind-fg:#8a5a00;--low-bg:#efeeea;--low-fg:#52514e;
--ok-bg:#dff3e9;--ok-fg:#0b6b46;--agg-bg:#fdeae2;--agg-fg:#a8441b;}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#121211;--surface:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--muted:#97968e;--line:#383835;--accent:#6da7ec;
--core-bg:#123d2c;--core-fg:#8fe0bb;--ded-bg:#16304f;--ded-fg:#9ec5f4;--ind-bg:#3d3011;--ind-fg:#f3cf7a;--low-bg:#2a2a28;--low-fg:#c3c2b7;--ok-bg:#123d2c;--ok-fg:#8fe0bb;--agg-bg:#43231a;--agg-fg:#f3a98a;}}
:root[data-theme="dark"]{--bg:#121211;--surface:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--muted:#97968e;--line:#383835;--accent:#6da7ec;
--core-bg:#123d2c;--core-fg:#8fe0bb;--ded-bg:#16304f;--ded-fg:#9ec5f4;--ind-bg:#3d3011;--ind-fg:#f3cf7a;--low-bg:#2a2a28;--low-fg:#c3c2b7;--ok-bg:#123d2c;--ok-fg:#8fe0bb;--agg-bg:#43231a;--agg-fg:#f3a98a;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1180px;margin:0 auto;padding:0 16px 64px}
header.top{padding:40px 0 16px}
h1{font-size:clamp(24px,4vw,36px);line-height:1.15;margin:0 0 8px;letter-spacing:-.01em}
.sub{color:var(--ink2);margin:0}
nav.toc{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);margin:16px 0 0;padding:10px 0;display:flex;gap:6px 16px;flex-wrap:wrap;font-size:14px}
section{margin-top:44px}
h2{font-size:22px;margin:0 0 14px;padding-top:8px}
h3.grp{font-size:17px;margin:28px 0 12px;color:var(--ink2)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-top:24px}
.kpi{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 16px;display:flex;flex-direction:column}
.kv{font-size:28px;font-weight:650;font-variant-numeric:tabular-nums}.kl{color:var(--ink2);font-size:13px}
.note{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--accent2);border-radius:8px;padding:12px 16px;color:var(--ink2);font-size:14px}
.prose{max-width:860px}.prose li{margin:6px 0}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:13.5px;min-width:1050px}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}
th{position:sticky;top:0;background:var(--surface);color:var(--ink2);font-weight:600;cursor:pointer;white-space:nowrap;user-select:none}
th.sorted-asc::after{content:" ▲";font-size:10px}th.sorted-desc::after{content:" ▼";font-size:10px}
tbody tr:hover{background:color-mix(in srgb,var(--accent) 6%,transparent)}
td.r,th.r{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.92em}
.badge,.src{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12px;font-weight:600;white-space:nowrap}
.lvl-core{background:var(--core-bg);color:var(--core-fg)}.lvl-ded{background:var(--ded-bg);color:var(--ded-fg)}
.lvl-ind{background:var(--ind-bg);color:var(--ind-fg)}.lvl-low,.lvl-none{background:var(--low-bg);color:var(--low-fg)}
.src-ok{background:var(--ok-bg);color:var(--ok-fg)}.src-agg{background:var(--agg-bg);color:var(--agg-fg)}
.na{color:var(--muted);font-style:italic}
.filters{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 12px}
.filters button{font:inherit;font-size:13px;padding:5px 12px;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer}
.filters button[aria-pressed="true"]{background:var(--ink);color:var(--surface);border-color:var(--ink)}
figure{margin:0 0 28px;background:#fcfcfb;border:1px solid var(--line);border-radius:10px;padding:8px}
figure img{width:100%;height:auto;display:block}
figcaption{color:#52514e;font-size:13px;padding:6px 8px 2px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:14px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px;display:flex;flex-direction:column;gap:6px;min-width:0}
.card header{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}
.card h4{margin:0;font-size:16px;line-height:1.3}
.card p{margin:0;overflow-wrap:anywhere}
.ids,.meta{font-size:13px;color:var(--ink2)}.cat{font-size:13px;font-weight:600;color:var(--ink2)}
.bud{font-size:14px}
.fin{border-top:1px solid var(--line);margin-top:6px;padding-top:8px}
.finhead{font-size:12.5px;color:var(--ink2);margin-bottom:6px!important}
.fin dl{display:grid;grid-template-columns:repeat(3,1fr);gap:6px 10px;margin:0}
.fin dt{font-size:11.5px;color:var(--muted)}.fin dd{margin:0;font-weight:600;font-variant-numeric:tabular-nums}
.small{font-size:12.5px;color:var(--ink2)}
details summary{cursor:pointer;font-size:13px;color:var(--accent);margin-top:4px}
ul.files{padding-left:18px;overflow-wrap:anywhere}
.prose{overflow-wrap:anywhere}
footer{margin-top:56px;color:var(--muted);font-size:13px;border-top:1px solid var(--line);padding-top:16px}
@media (max-width:600px){.cards{grid-template-columns:1fr}.fin dl{grid-template-columns:repeat(2,1fr)}body{font-size:14.5px}}
@media print{nav.toc{display:none}.card{break-inside:avoid}}
"""

JS = """
(function(){
  const t=document.getElementById('tbl'), tb=t.tBodies[0];
  t.querySelectorAll('th').forEach((th,i)=>th.addEventListener('click',()=>{
    const asc=!th.classList.contains('sorted-asc');
    t.querySelectorAll('th').forEach(h=>h.classList.remove('sorted-asc','sorted-desc'));
    th.classList.add(asc?'sorted-asc':'sorted-desc');
    const rows=[...tb.rows];
    rows.sort((a,b)=>{
      const A=a.cells[i],B=b.cells[i];
      const x=A.dataset.v!==undefined?A.dataset.v:A.textContent.trim();
      const y=B.dataset.v!==undefined?B.dataset.v:B.textContent.trim();
      const nx=parseFloat(x),ny=parseFloat(y);
      let r;
      if(!isNaN(nx)||!isNaN(ny)){ if(isNaN(nx))return 1; if(isNaN(ny))return -1; r=nx-ny; }
      else r=x.localeCompare(y,'pl');
      return asc?r:-r;});
    rows.forEach(r=>tb.appendChild(r));
  }));
  document.querySelectorAll('.filters button').forEach(b=>b.addEventListener('click',()=>{
    document.querySelectorAll('.filters button').forEach(x=>x.setAttribute('aria-pressed','false'));
    b.setAttribute('aria-pressed','true');
    const f=b.dataset.f;
    [...tb.rows].forEach(r=>{
      const lvl=r.cells[5].textContent.trim(), src=r.cells[10].textContent.trim();
      let show=true;
      if(f==='bud') show=['rdzeń','dedykowana oferta','pośredni'].includes(lvl);
      if(f==='core') show=lvl==='rdzeń';
      if(f==='ok') show=src==='raport';
      r.hidden=!show;});
  }));
})();
"""


def build():
    page = f"""<!doctype html>
<html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Polskie spółki IT</title>
<meta name="description" content="Zestawienie 20 polskich spółek IT dla firm (ERP, SaaS, wdrożenia, oprogramowanie dla budownictwa) z danymi KRS i finansowymi.">
<style>{CSS}</style></head>
<body><div class="wrap">
<header class="top">
<h1>Polskie spółki IT dla przedsiębiorstw: ERP, SaaS, wdrożenia i oprogramowanie dla budownictwa</h1>
<p class="sub">Stan na 20.11.2026 · kwoty w tys. PLN · dane jednostkowe (spółka matka), o ile nie zaznaczono inaczej</p>
{kpis()}
</header>
<nav class="toc"><a href="#metodologia">Metodologia</a><a href="#tabela">Tabela</a><a href="#wykresy">Wykresy</a><a href="#analiza">Analiza</a><a href="#spolki">Spółki</a><a href="#ograniczenia">Ograniczenia</a><a href="#pliki">Raporty i źródła</a></nav>

<section id="metodologia" class="prose"><h2>1. Metodologia</h2>
<ul>
<li><strong>Dobór.</strong> 20 podmiotów w czterech grupach: spółki IT z GPW (integratorzy i producenci ERP), producenci SaaS z GPW, prywatni dostawcy i wdrożeniowcy ERP oraz producenci oprogramowania dla budownictwa (kosztorysowanie, cenniki, BIM, ERP dla deweloperów i GW).</li>
<li><strong>Identyfikacja.</strong> Oficjalne API KRS i przeglądarka RDF były zablokowane dla adresu IP środowiska badawczego (strona „Przerwa techniczna” lub błąd 403). Numery KRS, NIP i REGON ustalono z kilku zgodnych źródeł wtórnych: rejestr.io, MSiG (imsig.pl), bizraport, stron spółek i raportów ESPI. <strong>Nie zostały potwierdzone w eKRS.</strong></li>
<li><strong>Dane finansowe, dwa poziomy wiarygodności.</strong>
  <ul>
  <li>{src_badge(COMPANIES[0])} Dane z formularzy RR ESPI, jednostkowych sprawozdań ESEF i stron IR. Zysk brutto ze sprzedaży i amortyzację odczytano ze sprawozdań.</li>
  <li>{src_badge(COMPANIES[-1])} Dane ze sprawozdań złożonych do KRS, odczytane pośrednio z serwisów rejestr.io, bizraport, aleo, firmy.ai i okredo. Niezweryfikowane, status badania nieznany.</li>
  </ul></li>
<li><strong>Rok.</strong> Ostatni pełny rok obrotowy, najczęściej 2025. Wyjątki: Text (04.2025–03.2026), Symfonia (10.2024–09.2025); dla trzech małych spółek 2024. Nie użyto okresów częściowych.</li>
<li><strong>Wskaźniki.</strong> Marża netto = zysk netto / przychody. Tam, gdzie spółka nie raportuje EBITDA, obliczono ją jako EBIT + amortyzacja.</li>
</ul></section>

<section id="tabela"><h2>2. Tabela zbiorcza</h2>
<div class="filters" role="group" aria-label="Filtr">
<button data-f="all" aria-pressed="true">Wszystkie</button>
<button data-f="bud" aria-pressed="false">Związek z budownictwem</button>
<button data-f="core" aria-pressed="false">Budownictwo – rdzeń</button>
<button data-f="ok" aria-pressed="false">Tylko dane z raportów</button></div>
<div class="tablewrap"><table id="tbl"><thead><tr>
<th class="r">#</th><th>Spółka</th><th>KRS</th><th>Kategoria</th><th>Główny produkt / usługa</th><th>Budownictwo</th><th>Rok</th>
<th class="r">Przychody</th><th class="r">Zysk netto</th><th class="r">Marża netto</th><th>Źródło</th><th>Raport</th>
</tr></thead><tbody>
{table_rows()}
</tbody></table></div>
<p class="small">Kliknij nagłówek kolumny, aby sortować. <em>agregator*</em> oznacza dane z serwisów zbierających sprawozdania KRS, do weryfikacji w RDF.</p>
</section>

<section id="wykresy"><h2>3. Wykresy</h2>
<figure><img src="{img('przychody_spolek.png')}" alt="Wykres słupkowy przychodów 20 spółek, posortowany malejąco"><figcaption>Przychody ze sprzedaży, posortowane malejąco. Zakreskowane słupki to dane z agregatora KRS.</figcaption></figure>
<figure><img src="{img('zysk_netto_spolek.png')}" alt="Wykres słupkowy zysku netto spółek, posortowany malejąco"><figcaption>Zysk (strata) netto, posortowany malejąco. Pominięto Sonetę, dla której zysku netto nie ustalono.</figcaption></figure>
<figure><img src="{img('przychody_i_zysk_netto.png')}" alt="Porównanie przychodów i zysku netto w dwóch panelach"><figcaption>Przychody i zysk netto. Dwa panele z osobnymi skalami, aby mniejsze spółki były czytelne; przy zysku podano marżę netto.</figcaption></figure>
</section>

<section id="analiza" class="prose"><h2>4. Analiza</h2>
<p><strong>Największe przychody.</strong> Asseco Poland (1,70 mld zł) i Comarch (ok. 1,42 mld zł jednostkowo*, 1,71 mld zł Grupa) wyraźnie wyprzedzają resztę. Dalej są Asseco Business Solutions (478 mln zł), Text (329 mln zł), Sygnity (252 mln zł), Vercom (241 mln zł) i Symfonia (228 mln zł*). Na poziomie grup Asseco ma 16,8 mld zł, a skonsolidowany Vercom (471 mln zł) wyprzedza Text.</p>
<p><strong>Najwyższa marża netto.</strong></p>
<ul>
<li>Dane z raportów: Sygnity 35,9%, Text 35,2%, Vercom 33,6%, ABS 27,9%, Asseco Poland 25,4%. U Sygnity, Vercom i Asseco Poland zysk netto przewyższa EBIT dzięki przychodom finansowym (u Asseco są to dywidendy od spółek zależnych).</li>
<li>Marża operacyjna (EBIT / przychody): najlepsze są Text (38,4%), Sygnity (34,5%) i ABS (30,5%).</li>
<li>Wśród danych z agregatorów najwyższe marże mają małe firmy budowlane: ArCADiasoft (40,2%) i Athenasoft (39,8%).</li>
<li>Straty mają Symfonia (−24,4%) i Develogic (−16,0%), czyli podmioty konsolidujące rynek ERP dla budownictwa.</li>
</ul>
<p><strong>Najsilniejszy związek z budownictwem.</strong></p>
<ul>
<li><span class="badge lvl-core">rdzeń</span> Athenasoft (Norma, Intercenbud), SEKOCENBUD, Datacomp IT (ZUZIA), Develogic, ArCADiasoft i Orgbud-Serwis. Łącznie ok. 56 mln zł przychodów, mniej niż jedna średnia spółka SaaS z GPW.</li>
<li><span class="badge lvl-ded">dedykowana oferta</span> Symfonia (przejęła Develogic w grudniu 2025) i Asseco Business Solutions (ERP dla budownictwa w Macrologic, Softlab i WAPRO).</li>
<li><span class="badge lvl-ind">pośredni</span> Comarch, Asseco Poland i enova365 (Soneta) mają wdrożenia u wykonawców, ale bez produktu branżowego.</li>
</ul>
<p><strong>Integratorzy, SaaS i ERP.</strong></p>
<ul>
<li>Integratorzy i wdrożeniowcy: Asseco Poland, Sygnity, IT.integro, częściowo Comarch i Forterro.</li>
<li>Czyści producenci SaaS: Text, Vercom, Shoper, iFirma. Mają najwyższe marże i model abonamentowy, ale żaden nie ma produktu dla budownictwa.</li>
<li>Producenci ERP: ABS, Symfonia, InsERT, Soneta, Streamsoft, Forterro, Comarch.</li>
</ul>
<div class="note"><strong>Wniosek dla segmentu budowlanego.</strong> Rynek dzieli się na małe, wyspecjalizowane i rentowne narzędzia (kosztorysowanie, ceny, BIM) oraz moduły w ogólnych ERP. Kompletnego, skalowalnego systemu ERP/SaaS dla generalnego wykonawcy (kosztorys, budżet, podwykonawcy, rozliczanie robót, flota) w Polsce prawie nie ma. Develogic, który jest najbliżej, jest mały i ma stratę, a Symfonia dopiero go integruje. To potencjalna nisza.</div>
</section>

<section id="spolki"><h2>5. Spółki – szczegóły</h2>
<p class="small">Legenda: <span class="badge lvl-core">rdzeń</span> budownictwo to główny rynek · <span class="badge lvl-ded">dedykowana oferta</span> osobny produkt lub oferta dla budownictwa · <span class="badge lvl-ind">pośredni</span> wdrożenia u firm budowlanych bez produktu branżowego · <span class="badge lvl-low">marginalny</span> / <span class="badge lvl-none">brak</span></p>
{cards()}
<p class="small" style="margin-top:14px"><strong>Odrzucony kandydat:</strong> Simple S.A. (SIMPLE.ERP, KRS 0000065743). Spółka nie jest już notowana, a nie znaleziono kwot za 2024 ani 2025, jedynie dynamikę z EMIS.</p>
</section>

<section id="ograniczenia" class="prose"><h2>6. Ograniczenia danych</h2>
<ol>
<li><strong>KRS, NIP i REGON nie zweryfikowane w eKRS</strong> (blokada IP). Datacomp IT: REGON nie ustalono, NIP tylko z regulaminu sklepu. Develogic: średnia pewność przypisania marki do numeru KRS.</li>
<li><strong>12 spółek prywatnych ma dane z agregatorów.</strong> Status badania jest nieznany, a etykiety lat bywają przesunięte. Rozbieżności między serwisami (Symfonia, Streamsoft, Orgbud, Datacomp) opisano w uwagach przy spółkach.</li>
<li><strong>Brak PDF dla spółek prywatnych.</strong> E-sprawozdania XML są dostępne tylko w RDF, który był zablokowany.</li>
<li><strong>Comarch.</strong> Spółka jest poza giełdą od 03.2025. Raport roczny 2025 zawiera tylko dane Grupy, bez zysku netto; dane jednostkowe pochodzą z agregatora.</li>
<li><strong>Różne lata obrotowe.</strong> Text kończy rok 31.03, Symfonia 30.09. Datacomp IT, ArCADiasoft i Orgbud mają dane za 2024. Rok Forterro przypisano na podstawie jednego źródła.</li>
<li><strong>Różne definicje przychodów.</strong> Asseco Poland i ABS raportują przychody operacyjne (MSSF); InsERT i ArCADiasoft przychody operacyjne z agregatora. Zysku brutto ze sprzedaży nie ma w układzie rodzajowym (Vercom, Shoper) ani w UoR (iFirma).</li>
<li><strong>EBITDA</strong> jest raportowana tylko przez Text i Shoper. Dla pozostałych spółek giełdowych obliczono ją jako EBIT + amortyzacja.</li>
<li><strong>Zdarzenia po dniu bilansowym.</strong> Shoper połączony z cyber_Folks (01.09.2026), Develogic przejęty przez Symfonię (12.2025).</li>
<li>Załącznik wspomniany w poleceniu nie był dostępny. Raport opiera się wyłącznie na źródłach publicznych.</li>
</ol></section>

<section id="pliki" class="prose"><h2>7. Pobrane raporty i źródła</h2>
<p>Pliki PDF leżą w katalogu <code>reports/</code> obok tego pliku. Linki działają, gdy HTML jest otwarty z katalogu <code>research/</code>.</p>
<ul class="files">{''.join(f'<li><a href="reports/{f}">{E(f)}</a> – {E(d)}</li>' for f, d in REPORTS)}</ul>
<p>Pozostałe pliki: <a href="spolki_it_polska_dane_finansowe.csv">spolki_it_polska_dane_finansowe.csv</a>, <a href="raport_spolki_it_polska.md">raport_spolki_it_polska.md</a>.</p>
<p><strong>Źródła oficjalne do weryfikacji:</strong> <a href="https://wyszukiwarka-krs.ms.gov.pl/" target="_blank" rel="noopener">wyszukiwarka KRS</a>, <a href="https://rdf-przegladarka.ms.gov.pl/" target="_blank" rel="noopener">przeglądarka dokumentów finansowych (RDF)</a>. Źródła dla każdej spółki są w jej karcie (sekcja 5, „Uwagi i źródła”) oraz w pliku CSV.</p>
</section>
<footer>Wygenerowano skryptem <code>build_html.py</code> z tych samych danych co CSV i wykresy.</footer>
</div>
<script>{JS}</script>
</body></html>"""
    path = os.path.join(HERE, "raport_spolki_it_polska.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    return path


if __name__ == "__main__":
    print(build())

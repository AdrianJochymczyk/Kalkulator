# -*- coding: utf-8 -*-
"""Pełny generator raportu (ok. 100 spółek): CSV, wykresy PNG, HTML i Markdown.

Dane:
  * build.py            – 20 spółek z pierwszej rundy (lista COMPANIES)
  * new/s1..s8.json     – spółki z drugiej rundy, po jednym pliku na segment
  * analysis.py         – teksty analizy (pisane po przejrzeniu danych)
Uruchomienie: python3 research/build_all.py
"""
import base64
import csv
import glob
import html
import json
import os
import re
import statistics

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import build
from build import HERE, NIE

SEGMENTS = [
    "Biura projektowe (BIM)",
    "Wdrożeniowcy ERP/CRM",
    "Producenci ERP",
    "Integratorzy i software house'y",
    "SaaS B2B",
    "Obieg dokumentów / BPM / KSeF",
    "Cyfryzacja budowy (contech, BIM/CAD)",
    "Kosztorysowanie, inżynieria i nieruchomości",
    "Chmura / data center / cyberbezpieczeństwo",
]
FILE_SEG = {"s1": 0, "s2": 1, "s3": 3, "s4": 4, "s5": 5, "s6": 6, "s7": 7, "s8": 8}
ORIG_SEG = {
    "Asseco Poland": 3, "Sygnity": 3, "Comarch": 2, "Asseco Business Solutions": 2, "Symfonia": 2,
    "InsERT": 2, "Forterro": 2, "Streamsoft": 2, "Soneta": 2, "IT.integro": 1, "Vercom": 4, "Shoper": 4,
    "Text": 4, "iFirma": 4, "Athenasoft": 7, "SEKOCENBUD": 7, "Datacomp": 7, "ORGBUD": 7,
    "ArCADiasoft": 6, "Develogic": 7,
}
LEVELS = ["rdzeń", "oferta dedykowana", "pośredni", "marginalny", "brak"]
NUM = ["przychody", "zysk_brutto_sprz", "ebit", "zysk_netto", "ebitda"]


def to_num(v):
    if v is None or v == "" or (isinstance(v, str) and v.strip().lower() in ("null", NIE)):
        return None
    if isinstance(v, (int, float)):
        return int(round(v))
    s = re.sub(r"[^\d,.\-−]", "", str(v)).replace("−", "-").replace(",", ".")
    try:
        return int(round(float(s)))
    except ValueError:
        return None


def norm_level(s):
    s = (s or "").strip().lower()
    for l in LEVELS:
        if s.startswith(l.split()[0]):
            return l
    return "brak"


def load():
    rows = []
    for c in build.COMPANIES:
        c = dict(c)
        c["segment_i"] = next(v for k, v in ORIG_SEG.items() if c["nazwa"].startswith(k))
        c["runda"] = 1
        rows.append(c)
    seen = {re.sub(r"\W", "", c["krs"]) for c in rows if c["krs"] != NIE}
    seen_names = {c["nazwa"].lower()[:12] for c in rows}
    dupes = []
    for f in sorted(glob.glob(os.path.join(HERE, "new", "s*.json"))):
        key = os.path.basename(f)[:2]
        with open(f, encoding="utf-8") as fh:
            data = json.load(fh)
        for d in data:
            c = {k: d.get(k) for k in ("nazwa", "krs", "nip", "regon", "siedziba", "www", "kategoria", "produkt", "opis",
                                       "budownictwo", "rok", "ebitda_uwagi", "waluta", "typ", "data_pub", "zrodlo_fin",
                                       "link_raportu", "plik", "uwagi", "forma_prawna")}
            for k in ("krs", "nip", "regon"):
                c[k] = re.sub(r"[^\d]", "", str(c[k] or "")) or NIE
            for k in NUM:
                c[k] = to_num(d.get(k))
            for k in ("nazwa", "siedziba", "www", "kategoria", "produkt", "opis", "budownictwo", "rok", "typ",
                      "data_pub", "link_raportu", "uwagi", "forma_prawna"):
                c[k] = str(c[k] or NIE).strip()
            c["ebitda_uwagi"] = c["ebitda_uwagi"] or ""
            c["waluta"] = c["waluta"] or "PLN"
            c["plik"] = c["plik"] or ""
            c["zrodlo_fin"] = "pierwotne" if str(c["zrodlo_fin"]).startswith("pierw") else "agregator"
            c["poziom_bud"] = norm_level(d.get("poziom_bud"))
            c["segment_i"] = FILE_SEG[key]
            c["runda"] = 2
            krs = c["krs"] if c["krs"] != NIE else None
            if (krs and krs in seen) or c["nazwa"].lower()[:12] in seen_names:
                dupes.append(c["nazwa"])
                continue
            if krs:
                seen.add(krs)
            seen_names.add(c["nazwa"].lower()[:12])
            rows.append(c)
    for c in rows:
        c["segment"] = SEGMENTS[c["segment_i"]]
        if c["krs"] != NIE and not c["krs"].startswith("0"):
            c["krs"] = c["krs"].zfill(10)
    return rows, dupes


def margin(c):
    if c["przychody"] and c["zysk_netto"] is not None:
        return c["zysk_netto"] / c["przychody"] * 100
    return None


def rj(krs):
    return f"https://rejestr.io/krs/{int(krs)}" if krs != NIE else ""


def fmt(v):
    return NIE if v is None else f"{v}"


# ------------------------------------------------------------------ CSV
COLS = build.COLS[:6] + ["segment"] + build.COLS[6:]


def write_csv(rows):
    path = os.path.join(HERE, "spolki_it_polska_dane_finansowe.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        for c in sorted(rows, key=lambda c: (c["segment_i"], -(c["przychody"] or -1))):
            m = margin(c)
            extra = [
                "jednostki: tys. PLN",
                f"źródło danych finansowych: {'raport/ESPI/ESEF (pierwotne)' if c['zrodlo_fin'] == 'pierwotne' else 'agregator danych z KRS / prasa - wymaga weryfikacji w RDF'}",
                f"poziom związku z budownictwem: {c['poziom_bud']}",
                f"zysk brutto ze sprzedaży: {fmt(c['zysk_brutto_sprz'])}",
                f"EBIT: {fmt(c['ebit'])}",
                f"EBITDA: {fmt(c['ebitda'])}" + (f" ({c['ebitda_uwagi']})" if c["ebitda_uwagi"] else ""),
                f"data publikacji: {c['data_pub']}",
                f"plik lokalny: {c['plik'] or 'brak'}",
                c["uwagi"],
            ]
            w.writerow([c["nazwa"], c["krs"], c["nip"], c["regon"], c["siedziba"], c["www"], c["segment"],
                        c["kategoria"], c["opis"], c["budownictwo"], c["rok"], fmt(c["przychody"]), fmt(c["zysk_netto"]),
                        f"{m:.1f}%" if m is not None else NIE, c["waluta"], c["typ"], rj(c["krs"]) or NIE,
                        c["link_raportu"], " | ".join(extra)])
    return path


# ------------------------------------------------------------------ wykresy
BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
HATCH = "////"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "hatch.color": "white", "hatch.linewidth": 0.8})


def short(n):
    n = n.split(" (")[0]
    for s in (" sp. z o.o. sp.k.", " sp. z o.o. sp. k.", " spółka z ograniczoną odpowiedzialnością", " sp. z o.o.",
              " S.A.", " SA", " sp. j.", " spółka akcyjna", " Sp. z o.o.", " sp.k.", " sp. k."):
        n = n.replace(s, "")
    n = n.replace("Asseco Business Solutions", "Asseco BS")
    return n[:34] + ("…" if len(n) > 34 else "")


def label(c):
    s = short(c["nazwa"])
    r = c["rok"]
    if r != "2025":
        s += f" ({'FY ' + r[-4:] if len(r) > 9 else r[:7]})"
    if c["zrodlo_fin"] == "agregator":
        s += " *"
    return s


def style_ax(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)


def legend_src(ax, color):
    ax.legend(handles=[Patch(facecolor=color, label="dane z raportu / ESPI / ESEF"),
                       Patch(facecolor=color, hatch=HATCH, label="* dane z agregatora KRS (do weryfikacji)")],
              loc="lower right", frameon=False, fontsize=9)


def nf(v):
    return (f"{v:,.1f}" if abs(v) >= 0.1 else f"{v:.3f}").replace(",", " ").replace(".", ",")


def tall_bar(rows, key, color, title, foot, fname):
    n = len(rows)
    fig, ax = plt.subplots(figsize=(11, max(5, 0.24 * n + 1.6)))
    ys = list(range(n))
    vals = [r[key] / 1000 for r in rows]
    bars = ax.barh(ys, vals, color=color, height=0.7, edgecolor=SURF, linewidth=1)
    for b, r in zip(bars, rows):
        if r["zrodlo_fin"] == "agregator":
            b.set_hatch(HATCH)
    ax.set_yticks(ys)
    ax.set_yticklabels([label(r) for r in rows], fontsize=8.5)
    ax.invert_yaxis()
    ax.set_ylim(n - 0.4, -0.6)
    span = max(abs(v) for v in vals)
    for y, v in zip(ys, vals):
        ax.text(v + (span * 0.008 if v >= 0 else -span * 0.008), y, nf(v), va="center",
                ha="left" if v >= 0 else "right", fontsize=7.5, color=INK2)
    lo = min(vals + [0])
    ax.set_xlim(lo - span * 0.12 if lo < 0 else 0, span * 1.1)
    if lo < 0:
        ax.axvline(0, color=INK2, linewidth=0.8)
    style_ax(ax)
    ax.xaxis.set_ticks_position("both")
    ax.tick_params(axis="x", labeltop=True)
    ax.set_xlabel("mln PLN")
    ax.set_title(title, loc="left", fontsize=13, color=INK, pad=24)
    legend_src(ax, color)
    fig.text(0.01, 0.004, foot, fontsize=8, color=INK2)
    fig.tight_layout(rect=(0, 0.012, 1, 1))
    p = os.path.join(HERE, "charts", fname)
    fig.savefig(p, dpi=130)
    plt.close(fig)
    return p


def chart_revenue(rows):
    r = sorted([c for c in rows if c["przychody"] is not None], key=lambda c: c["przychody"], reverse=True)
    miss = len(rows) - len(r)
    return tall_bar(r, "przychody", BLUE,
                    f"Przychody – ostatni pełny rok obrotowy, {len(r)} spółek (mln PLN)",
                    f"Rok 2025, chyba że zaznaczono inaczej. Pominięto {miss} spółek bez ustalonych przychodów. "
                    "Dane jednostkowe, o ile w CSV nie zaznaczono inaczej.", "przychody_spolek.png")


def chart_profit(rows):
    r = sorted([c for c in rows if c["zysk_netto"] is not None], key=lambda c: c["zysk_netto"], reverse=True)
    miss = len(rows) - len(r)
    return tall_bar(r, "zysk_netto", ORANGE,
                    f"Zysk (strata) netto – ostatni pełny rok obrotowy, {len(r)} spółek (mln PLN)",
                    f"Pominięto {miss} spółek bez ustalonego zysku netto. Asseco Poland: zysk zawiera dywidendy od spółek zależnych.",
                    "zysk_netto_spolek.png")


def chart_combined(rows):
    """Small multiples: jeden panel na segment, każdy z własną (liniową) skalą."""
    segs = [i for i in range(len(SEGMENTS)) if any(c["segment_i"] == i and c["przychody"] for c in rows)]
    ncol = 3
    nrow = (len(segs) + ncol - 1) // ncol
    per = [sorted([c for c in rows if c["segment_i"] == i and c["przychody"]], key=lambda c: -c["przychody"]) for i in segs]
    hmax = max(len(p) for p in per)
    fig, axes = plt.subplots(nrow, ncol, figsize=(19, nrow * (0.42 * hmax + 1.4)), squeeze=False)
    for ax in axes.flat[len(segs):]:
        ax.axis("off")
    for ax, i, grp in zip(axes.flat, segs, per):
        ys = list(range(len(grp)))
        h = 0.38
        rev = [c["przychody"] / 1000 for c in grp]
        net = [(c["zysk_netto"] or 0) / 1000 for c in grp]
        b1 = ax.barh([y - h / 2 for y in ys], rev, height=h, color=BLUE, edgecolor=SURF, linewidth=0.8)
        b2 = ax.barh([y + h / 2 for y in ys], net, height=h, color=ORANGE, edgecolor=SURF, linewidth=0.8)
        for bars in (b1, b2):
            for b, c in zip(bars, grp):
                if c["zrodlo_fin"] == "agregator":
                    b.set_hatch(HATCH)
        span = max(rev)
        for y, v, c in zip(ys, net, grp):
            m = margin(c)
            t = "zysk n/d" if m is None else f"{m:.1f}%".replace(".", ",")
            ax.text(max(v, 0) + span * 0.01, y + h / 2, t, va="center", fontsize=7, color=INK2)
        ax.set_yticks(ys)
        ax.set_yticklabels([label(c) for c in grp], fontsize=8)
        ax.set_ylim(hmax - 0.4, -0.6)
        lo = min(net + [0])
        ax.set_xlim(lo - span * 0.05 if lo < 0 else 0, span * 1.2)
        ax.axvline(0, color=INK2, linewidth=0.6)
        style_ax(ax)
        ax.set_title(SEGMENTS[i], loc="left", fontsize=11, color=INK)
        ax.set_xlabel("mln PLN", fontsize=8)
        ax.tick_params(axis="x", labelsize=8)
    fig.suptitle("Przychody vs zysk netto według segmentów (mln PLN; każdy panel ma własną skalę)",
                 x=0.01, ha="left", fontsize=14, color=INK)
    fig.legend(handles=[Patch(facecolor=BLUE, label="Przychody"), Patch(facecolor=ORANGE, label="Zysk (strata) netto"),
                        Patch(facecolor="#bbbbbb", hatch=HATCH, label="* dane z agregatora KRS (do weryfikacji)")],
               loc="upper right", ncol=3, frameon=False, fontsize=10)
    fig.text(0.01, 0.004, "Etykieta przy pomarańczowym słupku = marża netto. Panele nie są porównywalne wizualnie między sobą – porównuj wartości.",
             fontsize=8, color=INK2)
    fig.tight_layout(rect=(0, 0.01, 1, 0.97))
    p = os.path.join(HERE, "charts", "przychody_i_zysk_netto.png")
    fig.savefig(p, dpi=120)
    plt.close(fig)
    return p


def seg_stats(rows):
    out = []
    for i, s in enumerate(SEGMENTS):
        g = [c for c in rows if c["segment_i"] == i]
        rev = [c["przychody"] for c in g if c["przychody"] is not None]
        ms = [margin(c) for c in g if margin(c) is not None]
        out.append(dict(segment=s, n=len(g), n_rev=len(rev), suma=sum(rev), mediana=statistics.median(rev) if rev else None,
                        marza_med=statistics.median(ms) if ms else None,
                        bud=sum(1 for c in g if c["poziom_bud"] in ("rdzeń", "oferta dedykowana"))))
    return out


def chart_segments(rows):
    st = [s for s in seg_stats(rows) if s["n_rev"]]
    st.sort(key=lambda s: -s["mediana"])
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.2))
    ys = list(range(len(st)))
    for ax, key, col, ttl, f in ((axes[0], "mediana", BLUE, "Mediana przychodów w segmencie (mln PLN)", lambda v: nf(v / 1000)),
                                 (axes[1], "marza_med", ORANGE, "Mediana marży netto w segmencie (%)", lambda v: f"{v:.1f}%".replace(".", ","))):
        vals = [(s[key] or 0) / (1000 if key == "mediana" else 1) for s in st]
        ax.barh(ys, vals, color=col, height=0.62, edgecolor=SURF)
        ax.set_yticks(ys)
        ax.set_yticklabels([f"{s['segment']}  (n={s['n_rev']})" for s in st] if ax is axes[0] else [""] * len(st), fontsize=9)
        ax.invert_yaxis()
        span = max(abs(v) for v in vals) or 1
        for y, s, v in zip(ys, st, vals):
            raw = s[key]
            ax.text(v + span * 0.01, y, f(raw) if raw is not None else "n/d", va="center", fontsize=8.5, color=INK2)
        lo = min(vals + [0])
        ax.set_xlim(lo * 1.2 if lo < 0 else 0, span * 1.18)
        ax.axvline(0, color=INK2, linewidth=0.6)
        style_ax(ax)
        ax.set_title(ttl, loc="left", fontsize=11, color=INK)
    fig.suptitle("Porównanie segmentów (mediany są odporne na pojedyncze duże spółki)", x=0.01, ha="left", fontsize=13, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    p = os.path.join(HERE, "charts", "segmenty.png")
    fig.savefig(p, dpi=130)
    plt.close(fig)
    return p


# ------------------------------------------------------------------ HTML
E = html.escape


def img(name):
    with open(os.path.join(HERE, "charts", name), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def short_url(u):
    u = re.sub(r"^https?://(www\.)?", "", u)
    return u if len(u) <= 60 else u[:57] + "…"


def linkify(text):
    out, last = [], 0
    for m in re.finditer(r"https?://[^\s,)\];]+", text):
        u = m.group(0).rstrip(".;")
        out.append(E(text[last:m.start()]))
        out.append(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(short_url(u))}</a>')
        last = m.start() + len(u)
    out.append(E(text[last:]))
    return "".join(out)


def md_inline(s):
    """**pogrubienie** -> <strong>, reszta escapowana."""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", E(s))


def num(v):
    return f'<span class="na">{NIE}</span>' if v is None else f"{v:,.0f}".replace(",", "&nbsp;")


def pct(c):
    m = margin(c)
    return f"{m:.1f}%".replace(".", ",") if m is not None else f'<span class="na">{NIE}</span>'


LVCLS = {"rdzeń": "lvl-core", "oferta dedykowana": "lvl-ded", "pośredni": "lvl-ind", "marginalny": "lvl-low", "brak": "lvl-none"}


def badge(lvl):
    return f'<span class="badge {LVCLS[lvl]}">{E(lvl)}</span>'


def src_badge(c):
    if c["zrodlo_fin"] == "pierwotne":
        return '<span class="src src-ok" title="Dane odczytane z raportu rocznego / ESPI / ESEF">raport</span>'
    return '<span class="src src-agg" title="Dane z agregatora sprawozdań KRS lub prasy – wymagają weryfikacji">agregator*</span>'


def krs_link(c):
    return f'<a class="mono" href="{rj(c["krs"])}" target="_blank" rel="noopener">{c["krs"]}</a>' if c["krs"] != NIE else f'<span class="na">{NIE}</span>'


def url_or_text(u, txt=None):
    if u.startswith("http"):
        return f'<a href="{E(u)}" target="_blank" rel="noopener">{E(txt or short_url(u))}</a>'
    return f'<span class="na">{E(u)}</span>'


def table_rows(rows):
    out = []
    for i, c in enumerate(sorted(rows, key=lambda c: -(c["przychody"] if c["przychody"] is not None else -10**12)), 1):
        m = margin(c)
        out.append(f"""<tr data-seg="{c['segment_i']}" data-lvl="{E(c['poziom_bud'])}" data-src="{c['zrodlo_fin']}">
<td class="r">{i}</td><td><a href="#c{c['id']}"><strong>{E(c['nazwa'].split(' (')[0])}</strong></a></td><td>{krs_link(c)}</td>
<td>{E(c['segment'])}</td><td>{E(c['produkt'])}</td><td>{badge(c['poziom_bud'])}</td><td>{E(c['rok'])}</td>
<td class="r" data-v="{'' if c['przychody'] is None else c['przychody']}">{num(c['przychody'])}</td>
<td class="r" data-v="{'' if c['zysk_netto'] is None else c['zysk_netto']}">{num(c['zysk_netto'])}</td>
<td class="r" data-v="{'' if m is None else round(m, 2)}">{pct(c)}</td><td>{src_badge(c)}</td>
<td>{url_or_text(c['link_raportu'], 'link')}</td></tr>""")
    return "\n".join(out)


def card(c):
    fin = [("Przychody", c["przychody"]), ("Zysk brutto ze sprzedaży", c["zysk_brutto_sprz"]), ("EBIT", c["ebit"]),
           ("EBITDA", c["ebitda"]), ("Zysk netto", c["zysk_netto"])]
    dl = "".join(f"<div><dt>{k}</dt><dd>{num(v)}</dd></div>" for k, v in fin)
    pdf = f'<a href="{E(c["plik"])}">{E(os.path.basename(c["plik"]))}</a>' if c["plik"] else '<span class="na">brak lokalnego PDF</span>'
    return f"""<article class="card" id="c{c['id']}" data-seg="{c['segment_i']}" data-lvl="{E(c['poziom_bud'])}">
<header><h4>{E(c['nazwa'])}</h4>{badge(c['poziom_bud'])}</header>
<p class="ids">KRS {krs_link(c)} · NIP <span class="mono">{E(c['nip'])}</span> · REGON <span class="mono">{E(c['regon'])}</span></p>
<p class="meta">{E(c['siedziba'])} · {url_or_text(c['www'])}</p>
<p class="cat">{E(c['kategoria'])}</p><p>{E(c['opis'])}</p>
<p class="bud"><strong>Budownictwo:</strong> {linkify(c['budownictwo'])}</p>
<div class="fin"><p class="finhead">Rok {E(c['rok'])} · tys. {E(c['waluta'])} · {E(c['typ'])} {src_badge(c)}</p>
<dl>{dl}<div><dt>Marża netto</dt><dd>{pct(c)}</dd></div></dl>
{f'<p class="small">EBITDA: {E(c["ebitda_uwagi"])}</p>' if c['ebitda_uwagi'] else ''}
<p class="small">Data publikacji: {E(c['data_pub'])} · Dane: {url_or_text(c['link_raportu'])} · Plik: {pdf}</p></div>
<details><summary>Uwagi i źródła</summary><p class="small">{linkify(c['uwagi'])}</p></details></article>"""


def cards(rows):
    out = []
    for i, s in enumerate(SEGMENTS):
        g = sorted([c for c in rows if c["segment_i"] == i], key=lambda c: -(c["przychody"] or -1))
        if g:
            out.append(f'<h3 class="grp" id="seg{i}">{E(s)} <span class="cnt">{len(g)}</span></h3><div class="cards">'
                       + "\n".join(card(c) for c in g) + "</div>")
    return "\n".join(out)


def seg_table(rows):
    tr = []
    for s in seg_stats(rows):
        mm = "n/d" if s["marza_med"] is None else f"{s['marza_med']:.1f}%".replace(".", ",")
        tr.append(f"<tr><td>{E(s['segment'])}</td><td class='r'>{s['n']}</td><td class='r'>{num(s['suma'])}</td>"
                  f"<td class='r'>{num(s['mediana'])}</td><td class='r'>{mm}</td><td class='r'>{s['bud']}</td></tr>")
    return ("<div class='tablewrap'><table class='seg'><thead><tr><th>Segment</th><th class='r'>Spółek</th><th class='r'>Suma przychodów</th>"
            "<th class='r'>Mediana przychodów</th><th class='r'>Mediana marży netto</th><th class='r'>Rdzeń / oferta budowlana</th></tr></thead><tbody>"
            + "".join(tr) + "</tbody></table></div>")


def paras(blocks):
    out = []
    for b in blocks:
        if isinstance(b, list):
            out.append("<ul>" + "".join(f"<li>{md_inline(x)}</li>" for x in b) + "</ul>")
        elif b.startswith("!"):
            out.append(f'<div class="note">{md_inline(b[1:])}</div>')
        else:
            out.append(f"<p>{md_inline(b)}</p>")
    return "\n".join(out)


def build_html(rows, A):
    css = open(os.path.join(HERE, "assets_report.css"), encoding="utf-8").read()
    js = open(os.path.join(HERE, "assets_report.js"), encoding="utf-8").read()
    prim = sum(1 for c in rows if c["zrodlo_fin"] == "pierwotne")
    core = [c for c in rows if c["poziom_bud"] == "rdzeń"]
    ded = [c for c in rows if c["poziom_bud"] == "oferta dedykowana"]
    seg_opts = "".join(f'<option value="{i}">{E(s)}</option>' for i, s in enumerate(SEGMENTS))
    reports = "".join(f'<li><a href="reports/{E(f)}">{E(f)}</a></li>' for f in sorted(os.listdir(os.path.join(HERE, "reports"))))
    page = f"""<!doctype html>
<html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Polskie spółki IT</title>
<meta name="description" content="Zestawienie {len(rows)} polskich firm IT i cyfryzacji budownictwa (ERP, SaaS, wdrożenia, biura projektowe, BIM) z danymi KRS i finansowymi.">
<style>{css}</style></head><body><div class="wrap">
<header class="top">
<h1>Polskie spółki IT dla przedsiębiorstw i cyfryzacja budownictwa</h1>
<p class="sub">Stan na 20.11.2026 · {len(rows)} podmiotów w {len(SEGMENTS)} segmentach · kwoty w tys. PLN · dane jednostkowe, o ile nie zaznaczono inaczej</p>
<div class="kpis">
<div class="kpi"><span class="kv">{len(rows)}</span><span class="kl">firm w zestawieniu</span></div>
<div class="kpi"><span class="kv">{prim}</span><span class="kl">z danymi z raportów rocznych / ESPI</span></div>
<div class="kpi"><span class="kv">{len(core)}</span><span class="kl">z budownictwem jako rdzeniem działalności</span></div>
<div class="kpi"><span class="kv">{len(ded)}</span><span class="kl">z dedykowaną ofertą dla budownictwa</span></div>
</div></header>
<nav class="toc"><a href="#metodologia">Metodologia</a><a href="#tabela">Tabela</a><a href="#segmenty">Segmenty</a><a href="#wykresy">Wykresy</a><a href="#analiza">Analiza</a><a href="#spolki">Firmy</a><a href="#ograniczenia">Ograniczenia</a><a href="#pliki">Pliki</a></nav>
<section id="metodologia" class="prose"><h2>1. Metodologia</h2>{paras(A.METODOLOGIA)}</section>
<section id="tabela"><h2>2. Tabela zbiorcza</h2>
<div class="filters">
<label>Segment <select id="fseg"><option value="">wszystkie</option>{seg_opts}</select></label>
<label>Budownictwo <select id="flvl"><option value="">wszystkie</option><option value="bud">rdzeń + dedykowana + pośredni</option><option value="rdzeń">tylko rdzeń</option><option value="oferta dedykowana">tylko oferta dedykowana</option></select></label>
<label>Dane <select id="fsrc"><option value="">wszystkie</option><option value="pierwotne">tylko z raportów</option><option value="agregator">tylko z agregatorów</option></select></label>
<label class="grow">Szukaj <input id="fq" type="search" placeholder="nazwa, produkt, KRS…"></label>
<span id="fcount" class="small"></span></div>
<div class="tablewrap tall"><table id="tbl"><thead><tr>
<th class="r">#</th><th>Firma</th><th>KRS</th><th>Segment</th><th>Główny produkt / usługa</th><th>Budownictwo</th><th>Rok</th>
<th class="r">Przychody</th><th class="r">Zysk netto</th><th class="r">Marża netto</th><th>Źródło</th><th>Dane</th></tr></thead>
<tbody>{table_rows(rows)}</tbody></table></div>
<p class="small">Kliknij nagłówek, aby sortować; kliknij nazwę firmy, aby przejść do jej karty. „agregator*” – dane z serwisów zbierających sprawozdania KRS lub z prasy, do weryfikacji w RDF.</p></section>
<section id="segmenty"><h2>3. Segmenty</h2>{seg_table(rows)}
<figure><img src="{img('segmenty.png')}" alt="Mediany przychodów i marży netto według segmentów"><figcaption>Mediany przychodów i marży netto w segmentach.</figcaption></figure></section>
<section id="wykresy"><h2>4. Wykresy</h2>
<figure><img src="{img('przychody_spolek.png')}" alt="Przychody wszystkich firm, malejąco"><figcaption>Przychody, posortowane malejąco (zakreskowane – dane z agregatora).</figcaption></figure>
<figure><img src="{img('zysk_netto_spolek.png')}" alt="Zysk netto wszystkich firm, malejąco"><figcaption>Zysk (strata) netto, posortowany malejąco.</figcaption></figure>
<figure><img src="{img('przychody_i_zysk_netto.png')}" alt="Przychody i zysk netto w panelach według segmentów"><figcaption>Przychody i zysk netto według segmentów – każdy panel ma własną skalę.</figcaption></figure></section>
<section id="analiza" class="prose"><h2>5. Analiza</h2>{paras(A.ANALIZA)}</section>
<section id="spolki"><h2>6. Firmy – karty</h2>
<p class="small">Legenda: {badge('rdzeń')} budownictwo to główny rynek · {badge('oferta dedykowana')} osobny produkt/oferta dla budownictwa · {badge('pośredni')} klienci/wdrożenia budowlane bez produktu branżowego · {badge('marginalny')} · {badge('brak')}</p>
<p class="small segnav">{' · '.join(f'<a href="#seg{i}">{E(s)}</a>' for i, s in enumerate(SEGMENTS))}</p>
{cards(rows)}</section>
<section id="ograniczenia" class="prose"><h2>7. Ograniczenia danych</h2>{paras(A.OGRANICZENIA)}</section>
<section id="pliki" class="prose"><h2>8. Pliki i źródła</h2>
<p>Raporty PDF w katalogu <code>reports/</code> (linki działają, gdy HTML jest otwarty z katalogu <code>research/</code>):</p><ul class="files">{reports}</ul>
<p>Dane: <a href="spolki_it_polska_dane_finansowe.csv">spolki_it_polska_dane_finansowe.csv</a> · <a href="raport_spolki_it_polska.md">raport_spolki_it_polska.md</a>. Źródła każdej firmy – w jej karcie („Uwagi i źródła”) i w CSV.</p>
<p>Weryfikacja oficjalna: <a href="https://wyszukiwarka-krs.ms.gov.pl/" target="_blank" rel="noopener">wyszukiwarka KRS</a>, <a href="https://rdf-przegladarka.ms.gov.pl/" target="_blank" rel="noopener">RDF – dokumenty finansowe</a>.</p></section>
<footer>Wygenerowano skryptem <code>build_all.py</code> z tych samych danych co CSV i wykresy.</footer>
</div><script>{js}</script></body></html>"""
    p = os.path.join(HERE, "raport_spolki_it_polska.html")
    open(p, "w", encoding="utf-8").write(page)
    return p


# ------------------------------------------------------------------ Markdown
def md_blocks(blocks):
    out = []
    for b in blocks:
        if isinstance(b, list):
            out += [f"- {x}" for x in b] + [""]
        elif b.startswith("!"):
            out += [f"> {b[1:]}", ""]
        else:
            out += [b, ""]
    return "\n".join(out)


def mdc(s):
    return str(s).replace("|", "/").replace("\n", " ")


def mnum(v):
    return NIE if v is None else f"{v:,.0f}".replace(",", " ")


def build_md(rows, A):
    L = [f"# Polskie spółki IT dla przedsiębiorstw i cyfryzacja budownictwa", "",
         f"*Stan na 20.11.2026 · {len(rows)} podmiotów · kwoty w tys. PLN · dane jednostkowe, o ile nie zaznaczono inaczej. "
         "`*` = dane z agregatora KRS/prasy, do weryfikacji.*", "",
         "Pliki: [`raport_spolki_it_polska.html`](raport_spolki_it_polska.html) (wersja interaktywna) · "
         "[`spolki_it_polska_dane_finansowe.csv`](spolki_it_polska_dane_finansowe.csv) · [`charts/`](charts/) · [`reports/`](reports/)", "",
         "## 1. Metodologia", "", md_blocks(A.METODOLOGIA), "## 2. Segmenty", "",
         "| Segment | Spółek | Suma przychodów | Mediana przychodów | Mediana marży netto | Rdzeń / oferta budowlana |", "|---|---:|---:|---:|---:|---:|"]
    for s in seg_stats(rows):
        L.append(f"| {s['segment']} | {s['n']} | {mnum(s['suma'])} | {mnum(s['mediana'])} | "
                 f"{'n/d' if s['marza_med'] is None else ('%.1f%%' % s['marza_med']).replace('.', ',')} | {s['bud']} |")
    L += ["", "![Segmenty](charts/segmenty.png)", "", "## 3. Tabela zbiorcza", "",
          "| # | Firma | KRS | Segment | Główny produkt / usługa | Budownictwo | Rok | Przychody | Zysk netto | Marża | Dane |",
          "|---|---|---|---|---|---|---|---:|---:|---:|---|"]
    for i, c in enumerate(sorted(rows, key=lambda c: -(c["przychody"] if c["przychody"] is not None else -10**12)), 1):
        st = "*" if c["zrodlo_fin"] == "agregator" else ""
        m = margin(c)
        link = f"[link]({c['link_raportu']})" if c["link_raportu"].startswith("http") else NIE
        L.append(f"| {i} | {mdc(c['nazwa'].split(' (')[0])} | {c['krs']} | {c['segment']} | {mdc(c['produkt'])} | {c['poziom_bud']} | "
                 f"{mdc(c['rok'])} | {mnum(c['przychody'])}{st if c['przychody'] is not None else ''} | {mnum(c['zysk_netto'])}{st if c['zysk_netto'] is not None else ''} | "
                 f"{('%.1f%%' % m).replace('.', ',') if m is not None else NIE} | {link} |")
    L += ["", "## 4. Wykresy", "", "![Przychody](charts/przychody_spolek.png)", "", "![Zysk netto](charts/zysk_netto_spolek.png)", "",
          "![Przychody i zysk netto wg segmentów](charts/przychody_i_zysk_netto.png)", "", "## 5. Analiza", "", md_blocks(A.ANALIZA),
          "## 6. Firmy – dane szczegółowe", ""]
    for i, s in enumerate(SEGMENTS):
        g = sorted([c for c in rows if c["segment_i"] == i], key=lambda c: -(c["przychody"] or -1))
        if not g:
            continue
        L += [f"### {s} ({len(g)})", ""]
        for c in g:
            L += [f"**{c['nazwa']}** — {c['kategoria']}",
                  f"- KRS {c['krs']} · NIP {c['nip']} · REGON {c['regon']} · {c['siedziba']} · {c['www']}",
                  f"- {c['opis']}",
                  f"- Budownictwo ({c['poziom_bud']}): {c['budownictwo']}",
                  f"- Finanse {c['rok']} ({c['typ']}; {'raport' if c['zrodlo_fin'] == 'pierwotne' else 'agregator*'}): przychody {mnum(c['przychody'])}, "
                  f"zysk brutto ze sprzedaży {mnum(c['zysk_brutto_sprz'])}, EBIT {mnum(c['ebit'])}, EBITDA {mnum(c['ebitda'])}, zysk netto {mnum(c['zysk_netto'])}; "
                  f"dane: {c['link_raportu']}" + (f"; plik: `{c['plik']}`" if c["plik"] else ""),
                  f"- Uwagi: {c['uwagi']}", ""]
    L += ["## 7. Ograniczenia danych", "", md_blocks(A.OGRANICZENIA),
          "## 8. Weryfikacja oficjalna", "", "- https://wyszukiwarka-krs.ms.gov.pl/", "- https://rdf-przegladarka.ms.gov.pl/", ""]
    p = os.path.join(HERE, "raport_spolki_it_polska.md")
    open(p, "w", encoding="utf-8").write("\n".join(L))
    return p


def main():
    import analysis as A
    rows, dupes = load()
    for n, c in enumerate(sorted(rows, key=lambda c: (c["segment_i"], -(c["przychody"] or -1))), 1):
        c["id"] = n
    os.makedirs(os.path.join(HERE, "charts"), exist_ok=True)
    print(write_csv(rows))
    for f in (chart_revenue, chart_profit, chart_combined, chart_segments):
        print(f(rows))
    print(build_html(rows, A))
    print(build_md(rows, A))
    print("firm:", len(rows), "duplikaty pominięte:", dupes)
    return rows


if __name__ == "__main__":
    main()

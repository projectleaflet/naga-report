import json, re, base64, html, asyncio
import numpy as np
from content import REPORT as R

BG = "#0E100D"; RED = "#BE3126"; BONE = "#E8E4D6"; OLIVE = "#7E8166"; BROWN = "#412C24"
INK = "#14160F"; PAPER = "#E8E4D6"; PAPER2 = "#DED9C8"; MUTE = "#5E6150"

logo_b64 = base64.b64encode(open("logo_mark.png", "rb").read()).decode()
LOGO = f"data:image/png;base64,{logo_b64}"

# ---------- map ----------
UA = json.load(open("ukraine_map.json"))
COEF = np.array(json.load(open("proj.json")))
def proj(lo, la):
    x, y = np.array([lo, la, lo * la, 1]) @ COEF
    return float(x), float(y)

OCCUPIED = {"crimea", "luhansk"}  # heavier hatch tint for fully/mostly occupied
def map_svg():
    paths = []
    for l in UA["locations"]:
        fill = "#1A1D18" if l["id"] not in OCCUPIED else "#26221C"
        paths.append(f'<path d="{l["path"]}" fill="{fill}" stroke="{OLIVE}" stroke-width="0.8" stroke-opacity="0.7"/>')
    marks = []
    # front axes
    for name, lo, la, n in R["axes"]:
        x, y = proj(lo, la)
        r = 6 + n * 0.55
        marks.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="none" stroke="{BONE}" stroke-width="1.2" stroke-dasharray="3 2" opacity="0.85"/>')
        ax_off = {"Sloviansk": (-r-52, -2), "Lyman": (r+3, -4), "Kostiantynivka": (r+3, 6)}
        dx, dy = ax_off.get(name, (r+3, 3))
        marks.append(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" font-family="DejaVu Sans Mono" font-size="9" fill="{BONE}" opacity="0.85">{html.escape(name)} {n}</text>')
    # incidents
    label_offsets = {"Boyarka": (-8, 14), "Hlevakha": (-8, 26), "Kyiv": (8, -6), "Mykolaiv": (8, 10), "Kropyvnytskyi": (8, -4), "Kharkiv": (8, -6), "Lozova": (-48, 14), "Dnipro": (8, -6), "Zaporizhzhia": (8, 12), "Kramatorsk": (8, 16), "Sloviansk": (8, 4)}
    for name, lo, la, sev, lab in R["incidents"]:
        x, y = proj(lo, la)
        r = {1: 4, 2: 6, 3: 8.5}[sev]
        op = {1: 0.55, 2: 0.8, 3: 1}[sev]
        marks.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r*2.2:.1f}" fill="{RED}" opacity="{0.10*sev:.2f}"/>')
        marks.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{RED}" opacity="{op}" stroke="{BG}" stroke-width="1"/>')
        dx, dy = label_offsets.get(name, (8, 4))
        marks.append(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" font-family="DejaVu Sans" font-size="10" font-weight="bold" fill="{BONE}">{html.escape(name)}</text>')
    legend = f'''
    <g transform="translate(20 530)" font-family="DejaVu Sans Mono" font-size="10" fill="{BONE}">
      <rect x="-8" y="-16" width="260" height="128" fill="{BG}" stroke="{OLIVE}" stroke-width="0.8"/>
      <text x="0" y="0" font-size="11" font-weight="bold" fill="{RED}">LEGEND</text>
      <circle cx="8" cy="18" r="8.5" fill="{RED}"/><text x="24" y="22">Severe: deaths or mass damage</text>
      <circle cx="8" cy="40" r="6" fill="{RED}" opacity="0.8"/><text x="24" y="44">Moderate: casualties or infrastructure hit</text>
      <circle cx="8" cy="60" r="4" fill="{RED}" opacity="0.55"/><text x="24" y="64">Minor: region hit, limited detail</text>
      <circle cx="8" cy="82" r="8" fill="none" stroke="{BONE}" stroke-width="1.2" stroke-dasharray="3 2"/><text x="24" y="86">Front axis, clashes past 24h</text>
      <rect x="0" y="96" width="16" height="10" fill="#26221C" stroke="{OLIVE}" stroke-width="0.8"/><text x="24" y="105">Occupied or mostly occupied</text>
    </g>'''
    return f'<svg viewBox="0 0 1000 670" xmlns="http://www.w3.org/2000/svg" width="100%">{"".join(paths)}{"".join(marks)}{legend}</svg>'

# ---------- helpers ----------
def s(nums):  # source superscripts
    return '<span class="src">' + ",".join(str(n) for n in nums) + "</span>"

def paras(lst, srcs=None):
    out = "".join(f"<p>{html.escape(p)}</p>" for p in lst)
    if srcs:
        out = out[:-4] + " " + s(srcs) + "</p>"
    return out

LEVEL_CLASS = {"LOW": "lv-low", "MED": "lv-med", "HIGH": "lv-high", "SEVERE": "lv-sev"}

def oblast_rows():
    rows = []
    for o in R["oblasts"]:
        rows.append(f'''<div class="ob"><div class="ob-head"><span class="ob-name">{html.escape(o["name"])}</span><span class="lv {LEVEL_CLASS[o["level"]]}">{o["level"]}</span></div><p>{html.escape(o["text"])} {s(o["srcs"])}</p></div>''')
    return "".join(rows)

def key_numbers():
    return "".join(f'<div class="kn"><div class="kn-n">{n}</div><div class="kn-l">{html.escape(l)}</div></div>' for n, l in R["key_numbers"])

def headlines():
    out = []
    for t, outlet, n in R["headlines"]:
        url = next(u for i, _, u in R["sources"] if i == n)
        out.append(f'<li><a href="{html.escape(url)}">{html.escape(t)}</a> <span class="outlet">{html.escape(outlet)}</span></li>')
    return "".join(out)

def sources():
    return "".join(f'<li><span class="sn">{n}</span> {html.escape(t)} <a href="{html.escape(u)}">{html.escape(u)}</a></li>' for n, t, u in R["sources"])

def travel_rows():
    return "".join(f'<div class="tr"><div class="tr-k">{k}</div><div class="tr-v">{html.escape(v)} {s(src)}</div></div>' for k, v, src in R["travel"]["items"])

def incident_table():
    inc = sorted(R["incidents"], key=lambda t: -t[3])
    rows = "".join(f'<div class="ir"><span class="ir-dot s{sev}"></span><b>{html.escape(n)}</b><span>{html.escape(lab)}</span></div>' for n, lo, la, sev, lab in inc)
    return f'<div class="itab">{rows}</div>'

def footer(dark=False):
    return f'''<div class="foot {"foot-dark" if dark else ""}"><span>THE NAGA REPORT // {R["date_iso"]} // EDITION {R["edition"]}</span><span>PROJECTLEAFLET.COM / t.me/TheLeaflet</span></div>'''

def page_head(title):
    return f'''<div class="ph"><div class="ph-l"><img src="{LOGO}" class="ph-logo"/><span>THE NAGA REPORT</span></div><div class="ph-r">{html.escape(title)} // {R["date_iso"]}</div></div>'''

CSS = f'''
@page {{ size: Letter; margin: 0; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: "DejaVu Sans", sans-serif; color: {INK}; background: {PAPER}; font-size: 10.2pt; line-height: 1.38; }}
.page {{ width: 8.5in; height: 11in; padding: 0.5in 0.6in 0.7in; page-break-after: always; background: {PAPER}; position: relative; overflow: hidden; }}
.page .inner {{ height: calc(100% - 0.45in); overflow: hidden; }}
.page.dark {{ background: {BG}; color: {BONE}; }}
.mono {{ font-family: "DejaVu Sans Mono", monospace; }}
p {{ margin: 0 0 6px 0; }}
a {{ color: {RED}; text-decoration: none; }}
.dark a {{ color: #D9A59B; }}
.src {{ font-family: "DejaVu Sans Mono", monospace; font-size: 7pt; color: {RED}; vertical-align: super; letter-spacing: 0.02em; }}
h2 {{ font-family: "DejaVu Sans", sans-serif; font-weight: bold; font-size: 13pt; letter-spacing: 0.06em; text-transform: uppercase; margin: 14px 0 6px; padding-bottom: 4px; border-bottom: 2px solid {RED}; }}
h2:first-of-type {{ margin-top: 0; }}
.foot {{ position: absolute; left: 0.6in; right: 0.6in; bottom: 0.32in; display: flex; justify-content: space-between; font-family: "DejaVu Sans Mono", monospace; font-size: 7.5pt; color: {MUTE}; border-top: 1px solid {OLIVE}; padding-top: 5px; letter-spacing: 0.04em; }}
.foot-dark {{ color: {OLIVE}; }}
.ph {{ height: 0.3in; display: flex; justify-content: space-between; align-items: center; font-family: "DejaVu Sans Mono", monospace; font-size: 8pt; letter-spacing: 0.08em; color: {MUTE}; border-bottom: 1px solid {OLIVE}; padding-bottom: 6px; margin-bottom: 14px; }}
.ph-l {{ display: flex; align-items: center; gap: 8px; font-weight: bold; color: {INK}; }}
.dark .ph-l {{ color: {BONE}; }}
.dark .ph {{ color: {OLIVE}; }}
.ph-logo {{ height: 18px; filter: invert(1); }}
.dark .ph-logo {{ filter: none; }}

/* cover */
.cover {{ padding: 0; }}
.cover-top {{ background: {BG}; color: {BONE}; height: 4.75in; padding: 0.55in 0.6in 0.4in; border-bottom: 5px solid {RED}; position: relative; }}
.brand {{ display: flex; justify-content: space-between; align-items: flex-start; font-family: "DejaVu Sans Mono", monospace; font-size: 9pt; letter-spacing: 0.1em; color: {OLIVE}; }}
.brand b {{ color: {BONE}; }}
.cover-logo {{ height: 78px; }}
.title {{ margin-top: 22px; }}
.title .kick {{ font-family: "DejaVu Sans Mono", monospace; color: {OLIVE}; font-size: 10pt; letter-spacing: 0.18em; }}
.title h1 {{ font-size: 44pt; margin: 2px 0 0; letter-spacing: -0.01em; line-height: 1; color: {BONE}; }}
.title .sub {{ font-size: 13pt; color: {BONE}; margin-top: 8px; letter-spacing: 0.04em; }}
.meta {{ display: flex; gap: 34px; margin-top: 26px; font-family: "DejaVu Sans Mono", monospace; font-size: 8.5pt; color: {OLIVE}; letter-spacing: 0.06em; }}
.meta div b {{ display: block; color: {BONE}; font-size: 13pt; margin-top: 2px; letter-spacing: 0; }}
.risk {{ position: absolute; right: 0.6in; bottom: 0.4in; text-align: right; font-family: "DejaVu Sans Mono", monospace; letter-spacing: 0.12em; font-size: 8.5pt; color: {OLIVE}; }}
.risk b {{ display: block; font-size: 30pt; color: {RED}; letter-spacing: 0.06em; line-height: 1; margin-top: 4px; }}
.cover-body {{ padding: 0.35in 0.6in 0.4in; }}
.kns {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; margin: 0 0 16px; }}
.kn {{ border-left: 3px solid {RED}; padding: 2px 0 2px 8px; }}
.kn-n {{ font-family: "DejaVu Sans Mono", monospace; font-weight: bold; font-size: 19pt; color: {INK}; line-height: 1; }}
.kn-l {{ font-family: "DejaVu Sans Mono", monospace; font-size: 6.8pt; color: {MUTE}; text-transform: uppercase; letter-spacing: 0.04em; margin-top: 4px; line-height: 1.25; }}
.bl li {{ margin-bottom: 5px; }}
.bl {{ padding-left: 18px; margin: 4px 0 0; }}
.risknote {{ font-family: "DejaVu Sans Mono", monospace; font-size: 8pt; color: {MUTE}; margin-top: 10px; border-top: 1px dashed {OLIVE}; padding-top: 6px; }}

/* oblasts */
.obs {{ column-count: 2; column-gap: 22px; }}
.ob {{ break-inside: avoid; margin-bottom: 9px; }}
.ob-head {{ display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1px solid {OLIVE}; margin-bottom: 3px; }}
.ob-name {{ font-weight: bold; font-size: 10.5pt; letter-spacing: 0.02em; }}
.ob p {{ font-size: 9.4pt; line-height: 1.36; }}
.lv {{ font-family: "DejaVu Sans Mono", monospace; font-size: 7pt; letter-spacing: 0.1em; padding: 1px 6px; color: {BONE}; }}
.lv-low {{ background: {OLIVE}; }} .lv-med {{ background: {BROWN}; }} .lv-high {{ background: #8E2A20; }} .lv-sev {{ background: {RED}; }}

.two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
.tr {{ display: grid; grid-template-columns: 62px 1fr; gap: 10px; margin-bottom: 7px; }}
.tr-k {{ font-family: "DejaVu Sans Mono", monospace; font-weight: bold; font-size: 8.5pt; color: {RED}; letter-spacing: 0.08em; padding-top: 2px; }}
.tr-v {{ font-size: 9.6pt; }}
.watch li {{ margin-bottom: 4px; }}

/* map */
.mapwrap {{ margin-top: 6px; border: 1px solid {OLIVE}; padding: 6px; background: #0B0D0A; }}
.mapcap {{ font-family: "DejaVu Sans Mono", monospace; font-size: 8pt; color: {OLIVE}; margin-top: 8px; line-height: 1.5; }}

.itab {{ column-count: 2; column-gap: 24px; font-family: "DejaVu Sans Mono", monospace; font-size: 8.2pt; }}
.ir {{ display: grid; grid-template-columns: 12px 96px 1fr; gap: 6px; align-items: baseline; break-inside: avoid; padding: 3px 0; border-bottom: 1px solid #2A2E27; color: {BONE}; }}
.ir b {{ color: {BONE}; }}
.ir span:last-child {{ color: {OLIVE}; }}
.ir-dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: {RED}; }}
.ir-dot.s2 {{ opacity: 0.75; width: 7px; height: 7px; }} .ir-dot.s1 {{ opacity: 0.5; width: 5px; height: 5px; }}
/* headlines and sources */
.hl {{ padding-left: 24px; margin: 4px 0 0; }}
.hl li {{ margin-bottom: 4.5px; font-size: 9.8pt; }}
.outlet {{ font-family: "DejaVu Sans Mono", monospace; font-size: 7.5pt; color: {MUTE}; letter-spacing: 0.04em; }}
.srcs {{ list-style: none; padding: 0; margin: 4px 0 0; column-count: 3; column-gap: 20px; }}
.srcs li {{ font-size: 6.4pt; line-height: 1.3; margin-bottom: 3px; break-inside: avoid; color: {MUTE}; }}
.srcs a {{ color: {MUTE}; word-break: break-all; }}
.sn {{ font-family: "DejaVu Sans Mono", monospace; color: {RED}; font-weight: bold; }}
.method {{ font-size: 8.6pt; color: {MUTE}; border-top: 1px solid {OLIVE}; padding-top: 6px; margin-top: 10px; }}
.channels {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 8px; }}
.ch {{ border: 1px solid {OLIVE}; padding: 8px 10px; font-family: "DejaVu Sans Mono", monospace; font-size: 8pt; }}
.ch b {{ display: block; color: {RED}; letter-spacing: 0.1em; margin-bottom: 3px; }}
'''

HTML = f'''<!doctype html><html><head><meta charset="utf-8"><title>The Naga Report {R["date_iso"]}</title><style>{CSS}</style></head><body>

<div class="page cover">
  <div class="cover-top">
    <div class="brand"><div>PROJECT LEAFLET<br/><b>// DAILY SITUATION REPORT</b></div><img class="cover-logo" src="{LOGO}"/></div>
    <div class="title">
      <div class="kick">UKRAINE // EDITION {R["edition"]}</div>
      <h1>THE NAGA REPORT</h1>
      <div class="sub">{html.escape(R["date_long"])}</div>
    </div>
    <div class="meta">
      <div>DAY OF FULL-SCALE WAR<b>{R["day_of_war"]}</b></div>
      <div>COVERAGE<b>Nationwide</b></div>
      <div>DATA CUT<b>08:00 Kyiv</b></div>
    </div>
    <div class="risk">THREAT LEVEL, NEXT 24H<b>{R["risk"]}</b></div>
  </div>
  <div class="cover-body">
    <div class="kns">{key_numbers()}</div>
    <h2>Bottom line</h2>
    <ol class="bl">{"".join(f"<li>{html.escape(b)}</li>" for b in R["bottom_line"])}</ol>
    <div class="risknote">THREAT LEVEL BASIS: {html.escape(R["risk_note"])}<br/>{html.escape(R["cutoff"])}</div>
  </div>
  {footer()}
</div>

<div class="page">
  {page_head("OVERNIGHT AND OBLAST PICTURE")}<div class="inner">
  <h2>{html.escape(R["overnight"]["title"])}</h2>
  {paras(R["overnight"]["body"], R["overnight"]["srcs"])}
  <h2>Oblast by oblast</h2>
  <div class="obs">{oblast_rows()}</div>
  </div>{footer()}
</div>

<div class="page">
  {page_head("FRONT, STRIKES, NAVAL, TRAVEL")}<div class="inner">
  <h2>{html.escape(R["front"]["title"])}</h2>
  {paras(R["front"]["body"], R["front"]["srcs"])}
  <h2>{html.escape(R["ua_strikes"]["title"])}</h2>
  {paras(R["ua_strikes"]["body"], R["ua_strikes"]["srcs"])}
  <div class="two">
    <div><h2>{html.escape(R["naval"]["title"])}</h2>{paras(R["naval"]["body"], R["naval"]["srcs"])}</div>
    <div><h2>Watch list</h2><ul class="watch">{"".join(f"<li>{html.escape(w)}</li>" for w in R["watch"])}</ul></div>
  </div>
  <h2>{html.escape(R["travel"]["title"])}</h2>
  {travel_rows()}
  </div>{footer()}
</div>

<div class="page dark">
  {page_head("INCIDENT MAP")}
  <h2 style="border-color:{RED};color:{BONE}">Incident map, 24h to 08:00 Kyiv</h2>
  <div class="mapwrap">{map_svg()}</div>
  <div class="mapcap">Marker size reflects reported severity in the window, not strike count. Dashed rings mark front-line axes with General Staff clash counts for the past day. Oblast boundaries: @svg-maps/ukraine (CC BY 4.0). Positions approximate. Graphic: Project Leaflet.</div>
  <h2 style="border-color:{RED};color:{BONE};margin-top:14px">Incident ledger</h2>
  {incident_table()}
  {footer(dark=True)}
</div>

<div class="page">
  {page_head("HEADLINES AND SOURCES")}<div class="inner">
  <h2>Key media updates, last 36h</h2>
  <ol class="hl">{headlines()}</ol>
  <h2>Sources consulted</h2>
  <ol class="srcs">{sources()}</ol>
  <div class="method"><b>Method.</b> Compiled from Ukrainian official statements (Air Force, General Staff, oblast administrations, Ukrzaliznytsia, Ukrenergo) as carried by Ukrainian and international outlets, plus ISW. Russian MoD claims are marked as claims. Casualty figures are the latest available at cut-off and usually rise. Threat level is an editorial call built on four inputs: overnight munitions count, regions hit, civilian casualties, and transport or energy disruption.</div>
  <div class="channels">
    <div class="ch"><b>WEBSITE</b>projectleaflet.com<br/>The Daily Sitrep, Cold Files</div>
    <div class="ch"><b>TELEGRAM</b>t.me/TheLeaflet<br/>OSINT drops through the day</div>
    <div class="ch"><b>INSTAGRAM</b>@projectleaflet<br/>@projectleaflet2.0</div>
  </div>
  </div>{footer()}
</div>
</body></html>'''

open("naga_report.html", "w").write(HTML)

async def render():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        await pg.goto("file:///home/claude/naga/naga_report.html")
        report = await pg.evaluate("""() => {
          const out=[];
          document.querySelectorAll('.page .inner').forEach((el,i)=>{
            let fs=100; el.style.zoom=fs+'%';
            while (el.scrollHeight > el.clientHeight + 1 && fs > 72) { fs -= 2; el.style.zoom = fs+'%'; }
            out.push({page:i+2, fs, overflow: el.scrollHeight > el.clientHeight + 1});
          });
          return out; }""")
        print(report)
        foot = f'<div style="border-top:1px solid {OLIVE};padding-top:5px;display:flex;justify-content:space-between;font-family:DejaVu Sans Mono;font-size:7.5px;color:{MUTE};letter-spacing:0.04em"><span>THE NAGA REPORT // {R["date_iso"]} // EDITION {R["edition"]}</span><span>PROJECTLEAFLET.COM / t.me/TheLeaflet &nbsp; PAGE <span class="pageNumber"></span>/<span class="totalPages"></span></span></div>'
        await pg.pdf(path=f"Naga_Report_{R['date_iso']}.pdf", format="Letter", print_background=True, prefer_css_page_size=True, display_header_footer=False)
        await b.close()
asyncio.run(render())
print("ok")

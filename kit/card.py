import asyncio, base64
from content import REPORT as R
BG="#0E100D"; RED="#BE3126"; BONE="#E8E4D6"; OLIVE="#7E8166"
LOGO="data:image/png;base64,"+base64.b64encode(open("logo_mark.png","rb").read()).decode()
H=f'''<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;background:{BG};width:1200px;height:630px;overflow:hidden;font-family:"DejaVu Sans Mono",monospace;color:{BONE};position:relative}}
.top{{position:absolute;top:0;left:0;right:0;height:6px;background:{RED}}}
.hdr{{position:absolute;top:34px;left:48px;font-size:22px;font-weight:bold;letter-spacing:.06em}}
.hdr small{{display:block;font-size:14px;color:{OLIVE};font-weight:normal;margin-top:4px}}
.ed{{position:absolute;top:34px;right:48px;text-align:right;font-size:14px;color:{RED};letter-spacing:.08em}}
.ed small{{display:block;color:{OLIVE};margin-top:6px}}
.logo{{position:absolute;top:118px;right:48px;height:84px}}
.kick{{position:absolute;top:126px;left:48px;font-size:28px;color:{OLIVE};font-family:"DejaVu Sans";font-weight:bold;letter-spacing:.02em}}
.h1{{position:absolute;top:164px;left:48px;font-size:54px;font-family:"DejaVu Sans";font-weight:bold;letter-spacing:-.01em;line-height:1}}
.nums{{position:absolute;top:262px;left:48px;display:flex;gap:70px}}
.n b{{display:block;font-size:92px;color:{RED};font-weight:bold;line-height:1;letter-spacing:-.02em}}
.n span{{display:block;font-size:14px;color:{OLIVE};line-height:1.35;margin-top:8px;letter-spacing:.04em}}
.ret{{position:absolute;top:290px;right:60px;width:140px;height:140px}}
.line{{position:absolute;top:452px;left:48px;right:48px;font-size:21px;font-weight:bold;letter-spacing:.02em}}
.src{{position:absolute;top:490px;left:48px;font-size:14px;color:{OLIVE}}}
.rule{{position:absolute;top:538px;left:48px;right:48px;border-top:1px solid #2E3129}}
.ft{{position:absolute;top:552px;left:48px;right:48px;display:flex;justify-content:space-between;font-size:14px;color:{OLIVE};letter-spacing:.04em}}
</style></head><body>
<div class="top"></div>
<div class="hdr">PROJECT LEAFLET<small>// THE NAGA REPORT</small></div>
<div class="ed">EDITION {R["edition"]}<small>{R["date_iso"]}</small></div>
<img class="logo" src="{LOGO}"/>
<div class="kick">DAILY SITUATION REPORT, UKRAINE</div>
<div class="h1">TEN REGIONS IN ONE NIGHT</div>
<div class="nums">
 <div class="n"><b>172</b><span>STRIKE UAVS LAUNCHED<br/>147 NEUTRALIZED</span></div>
 <div class="n"><b>6/38</b><span>CIVILIANS KILLED / WOUNDED<br/>PAST 24 HOURS</span></div>
 <div class="n"><b>16h+</b><span>WORST PASSENGER<br/>RAIL DELAY</span></div>
</div>
<svg class="ret" viewBox="0 0 140 140"><circle cx="70" cy="70" r="60" fill="none" stroke="{RED}" stroke-width="2" opacity=".9"/><circle cx="70" cy="70" r="22" fill="none" stroke="{RED}" stroke-width="2"/><line x1="70" y1="0" x2="70" y2="40" stroke="{RED}" stroke-width="2"/><line x1="70" y1="100" x2="70" y2="140" stroke="{RED}" stroke-width="2"/><line x1="0" y1="70" x2="40" y2="70" stroke="{RED}" stroke-width="2"/><line x1="100" y1="70" x2="140" y2="70" stroke="{RED}" stroke-width="2"/></svg>
<div class="line">ZAPORIZHZHIA HARDEST HIT / 238 CLASHES / THREAT LEVEL: HIGH</div>
<div class="src">SOURCES: UKRAINIAN AIR FORCE / GENERAL STAFF / KYIV INDEPENDENT / UKRINFORM / ISW</div>
<div class="rule"></div>
<div class="ft"><span>t.me/TheLeaflet</span><span>PROJECTLEAFLET.COM / THE NAGA REPORT</span></div>
</body></html>'''
open("card.html","w").write(H)
async def run():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={"width":1200,"height":630})
        await pg.goto("file:///home/claude/naga/card.html")
        await pg.screenshot(path=f"Naga_Report_{R['date_iso']}_card.png", type="png")
        await b.close()
asyncio.run(run())

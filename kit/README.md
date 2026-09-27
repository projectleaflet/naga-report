# Naga Report build kit
- content.py: the day's report as a dict (edit this, or generate it each run). No em dashes.
- build.py: renders content.py to Naga_Report_<date>.pdf (Letter, 5 pages, auto-shrinks pages 2/3/5 to fit). Needs playwright+chromium, numpy, DejaVu fonts.
- card.py: renders the 1200x630 stat card PNG.
- ukraine_map.json + proj.json: oblast outlines (@svg-maps/ukraine, CC BY 4.0) and a fitted lon/lat->SVG projection for placing markers.
- logo_mark.png: official PL mark (white on transparent), pulled from the live site logo.
Palette: bg #0E100D, PL red #BE3126, bone #E8E4D6, olive #7E8166, brown #412C24.
Threat scale: ELEVATED / HIGH / SEVERE / CRITICAL from overnight munitions, regions hit, civilian casualties, transport/energy disruption.

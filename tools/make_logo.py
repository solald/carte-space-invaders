#!/usr/bin/env python3
"""Génère le logo Space Invader du site :
   - invader.svg  : favicon (onglet + petits aperçus)
   - og_card.html : carte d'aperçu de partage 1200x630 (rasterisée en og-image.png via Chrome)
Lancer depuis la racine du repo :  python3 tools/make_logo.py
"""

# Classic "crab" Space Invader, grille 11x8 (1 = pixel plein)
GRID = [
    "00100000100",
    "00010001000",
    "00111111100",
    "01101110110",
    "11111111111",
    "10111111101",
    "10100000101",
    "00011011000",
]
ACCENT = "#3358d4"
BG = "#eef1f5"


def invader_rects(cell, x0, y0, color):
    """Renvoie les <rect> SVG de l'invader, pixel par pixel."""
    out = []
    for r, row in enumerate(GRID):
        for c, ch in enumerate(row):
            if ch == "1":
                x = x0 + c * cell
                y = y0 + r * cell
                out.append(
                    f'<rect x="{x:g}" y="{y:g}" width="{cell:g}" height="{cell:g}" fill="{color}"/>'
                )
    return "\n".join(out)


def make_favicon():
    """Favicon carré : fond arrondi accent, invader blanc centré."""
    size = 44
    cell = 3
    w = 11 * cell          # 33
    h = 8 * cell           # 24
    x0 = (size - w) / 2    # 5.5
    y0 = (size - h) / 2    # 10
    rects = invader_rects(cell, x0, y0, "#ffffff")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" shape-rendering="crispEdges">
<rect x="0" y="0" width="{size}" height="{size}" rx="9" fill="{ACCENT}"/>
{rects}
</svg>
'''
    open("invader.svg", "w", encoding="utf-8").write(svg)
    print("written invader.svg")


def make_og_card():
    """Carte d'aperçu 1200x630 : invader accent + wordmark, fond clair."""
    # invader autonome (transparent) pour l'afficher en grand dans la carte
    cell = 16
    w = 11 * cell
    h = 8 * cell
    inv = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" shape-rendering="crispEdges">
{invader_rects(cell, 0, 0, ACCENT)}
</svg>'''
    html = f'''<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>
  html,body{{margin:0;padding:0}}
  .card{{width:1200px;height:630px;background:
        radial-gradient(1200px 700px at 50% -10%, #ffffff 0%, {BG} 60%);
        display:flex;flex-direction:column;align-items:center;justify-content:center;
        font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
        color:#1c2430}}
  .inv{{margin-bottom:34px;filter:drop-shadow(0 10px 24px rgba(51,88,212,.28))}}
  h1{{font-size:74px;margin:0;font-weight:800;letter-spacing:.5px}}
  h1 span{{color:{ACCENT}}}
  p{{font-size:30px;margin:18px 0 0;color:#5d6b7e;font-weight:500}}
  .pill{{margin-top:30px;font-size:22px;color:{ACCENT};background:#e7ecfb;
        border:1px solid #cfd9f6;padding:10px 22px;border-radius:999px;font-weight:600}}
</style></head>
<body><div class="card">
  <div class="inv">{inv}</div>
  <h1>Cartes <span>Space Invaders</span></h1>
  <p>Repère, flashe et coche les mosaïques ville par ville</p>
  <div class="pill">Marseille · Paris · PACA</div>
</div></body></html>'''
    open("og_card.html", "w", encoding="utf-8").write(html)
    print("written og_card.html")


if __name__ == "__main__":
    make_favicon()
    make_og_card()

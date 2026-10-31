#!/usr/bin/env python3
"""Contribution heatmap that gathers into an ASCII blue whale, dives, resurfaces."""
from __future__ import annotations
import json, subprocess, datetime as dt
from html import escape

CELL = 11.0
GAP  = 1.4
PITCH = CELL + GAP
COLS, ROWS = 53, 7
CYCLE = 18.0

# 时间轴
T = dict(hold=0.10, gather=0.30, hover=0.46, sink=0.58, rise=0.78, scatter=0.90)

WHALE_SCALE = 1.02

GREEN = ["#21262d", "#0e4429", "#006d32", "#26a641", "#39d353"]
BLUE  = ["#1b2a4a", "#1f4b8f", "#2f7ad6", "#58a6ff", "#9ecbff"]

def level(n: int) -> int:
    if n <= 0: return 0
    if n <= 2: return 1
    if n <= 5: return 2
    if n <= 9: return 3
    return 4

def fetch_days():
    q = """query{user(login:"jryang1997"){contributionsCollection{contributionCalendar{
        totalContributions weeks{contributionDays{date contributionCount}}}}}}"""
    out = subprocess.run(["gh","api","graphql","-f",f"query={q}"], capture_output=True, text=True)
    d = json.loads(out.stdout)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [d0 for w in d["weeks"] for d0 in w["contributionDays"]]
    return days[-371:] if len(days) > 371 else days, d["totalContributions"]

def main():
    days, total = fetch_days()
    while len(days) < COLS*ROWS:
        days.insert(0, {"date":"", "contributionCount":0})

    whale = json.load(open("assets/whale-points.json"))
    pts = whale["pts"]                      # 已按热力格顺序一一对应
    ww, wh = max(p[0] for p in pts)*WHALE_SCALE, max(p[1] for p in pts)*WHALE_SCALE

    CARD_W, CARD_H = 900, 560
    WIN = (8, 8, CARD_W-16, CARD_H-16)
    TOP = 34

    grid_w = COLS*PITCH - GAP
    grid_h = ROWS*PITCH - GAP
    gx = (CARD_W - grid_w)/2
    gy = 226

    wx = (CARD_W - ww)/2
    wy = 186
    SINK = 130

    def esc(s): return escape(str(s), quote=False)
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_W}" height="{CARD_H}" '
             f'viewBox="0 0 {CARD_W} {CARD_H}" role="img" aria-label="Contribution heatmap that gathers into an ASCII blue whale">')
    o.append('''<style>
:root{--bg:#0d1117;--bar:#161b22;--bd:#30363d;--fg:#e6edf3;--mu:#8b949e;--sav:#6e7681;--gr:#7ee787;--am:#e3b341;}
.m{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace}
</style>''')
    x,y,w,h = WIN
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="var(--bg)" stroke="var(--bd)" stroke-width="1.5"/>')
    o.append(f'<path d="M{x+10} {y} h{w-20} a10,10 0 0 1 10,10 v{TOP-10} h-{w} v-{TOP-10} a10,10 0 0 1 10,-10 z" fill="var(--bar)"/>')
    o.append(f'<path d="M{x+10} {y+TOP} H{x+w-10}" stroke="var(--bd)" stroke-width="1"/>')
    for i,c in enumerate(["#ff5f57","#febc2e","#28c840"]):
        o.append(f'<circle cx="{x+20+i*15}" cy="{y+16}" r="4.5" fill="{c}" opacity="0.9"/>')
    o.append(f'<text class="m" x="{x+w/2}" y="{y+20}" text-anchor="middle" font-size="11" fill="var(--mu)">'
             f'jryang1997@github: ~ — contributions.log</text>')

    # 水面（ASCII 波浪），鲸鱼下潜/上浮经过
    surface_y = wy + wh + 12
    waves = "".join("~" if i%3 else " " for i in range(96))
    o.append(f'<text class="m" x="{CARD_W/2}" y="{surface_y:.1f}" text-anchor="middle" '
             f'font-size="11" fill="#1f4b8f" xml:space="preserve">{esc(waves)}</text>')

    # 入水/出水：外层容器整体俯冲、没入水面、仰角浮出
    cx_, cy_ = wx + ww / 2, wy + wh / 2
    o.append("<g>")
    o.append(f'<animateTransform attributeName="transform" type="translate" additive="sum" '
             f'values="0 0;0 0;0 {SINK};0 {SINK};0 0;0 0" '
             f'keyTimes="0;0.46;0.58;0.66;0.78;1" dur="{CYCLE}s" repeatCount="indefinite"/>')
    o.append(f'<animateTransform attributeName="transform" type="rotate" additive="sum" '
             f'values="0 {cx_:.0f} {cy_:.0f};0 {cx_:.0f} {cy_:.0f};12 {cx_:.0f} {cy_:.0f};'
             f'12 {cx_:.0f} {cy_:.0f};-9 {cx_:.0f} {cy_:.0f};0 {cx_:.0f} {cy_:.0f}" '
             f'keyTimes="0;0.46;0.58;0.66;0.78;1" dur="{CYCLE}s" repeatCount="indefinite"/>')
    o.append(f'<animate attributeName="opacity" values="1;1;1;0;0;1;1" '
             f'keyTimes="0;0.46;0.52;0.58;0.64;0.70;1" dur="{CYCLE}s" repeatCount="indefinite"/>')

    # 格子
    for i in range(COLS*ROWS):
        col, row = i // ROWS, i % ROWS
        sx = gx + col*PITCH
        sy = gy + row*PITCH
        d = days[i]
        lv = level(d["contributionCount"])
        tx, ty = wx + pts[i][0], wy + pts[i][1]
        g_c, b_c = GREEN[lv], BLUE[max(2, lv)]

        vals = (f"{sx:.1f} {sy:.1f};{tx:.1f} {ty:.1f};{tx:.1f} {ty:.1f};"
                f"{tx:.1f} {ty:.1f};{tx:.1f} {ty:.1f};{sx:.1f} {sy:.1f};{sx:.1f} {sy:.1f}")
        kts = ";".join(f"{v:.3f}" for v in [0, T['gather'], T['hover'], T['sink'], T['rise'], T['scatter'], 1])
        fvals = f"{g_c};{b_c};{b_c};{BLUE[1]};{b_c};{g_c};{g_c}"

        o.append(f'<rect x="0" y="0" width="{CELL}" height="{CELL}" rx="2" fill="{g_c}">')
        o.append(f'<animateTransform attributeName="transform" type="translate" values="{vals}" '
                 f'keyTimes="{kts}" dur="{CYCLE}s" repeatCount="indefinite"/>')
        o.append(f'<animate attributeName="fill" values="{fvals}" keyTimes="{kts}" dur="{CYCLE}s" repeatCount="indefinite"/>')
        o.append('</rect>')

    o.append("</g>")

    # 底部统计
    sb_y = y + h - 26
    o.append(f'<path d="M{x+10} {sb_y-14} H{x+w-10}" stroke="var(--bd)" stroke-width="1"/>')
    o.append(f'<text class="m" x="{x+14}" y="{sb_y+4}" font-size="10" fill="var(--mu)">'
             f'{esc(total)} contributions · last 12 months</text>')
    o.append(f'<text class="m" x="{x+w-14}" y="{sb_y+4}" font-size="10" fill="var(--sav)" text-anchor="end">'
             f'{COLS}×{ROWS} cells → 1 blue whale</text>')
    o.append('</svg>')
    open("assets/contrib-ocean.svg","w",encoding="utf-8").write("\n".join(o))
    print("wrote assets/contrib-ocean.svg", len("\n".join(o)), "bytes; total", total)

if __name__ == "__main__":
    main()

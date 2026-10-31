#!/usr/bin/env python3
"""Build a GitHub-safe heatmap morph using poses baked from dsh-ascii-whales."""
from __future__ import annotations

import json
import subprocess
import xml.etree.ElementTree as ET
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLS, ROWS = 53, 7
CELL, PITCH = 10.0, 12.4
WIDTH, HEIGHT, CYCLE = 900, 400, 28
GREEN = ["#21262d", "#0e4429", "#006d32", "#26a641", "#39d353"]
LEVELS = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]
EASE = "0.77 0 0.175 1"


def fetch_days():
    query = '''query{user(login:"jryang1997"){contributionsCollection{contributionCalendar{
      totalContributions weeks{contributionDays{date weekday contributionCount contributionLevel}}}}}}'''
    result = subprocess.run(["gh", "api", "graphql", "-f", f"query={query}"],
                            capture_output=True, text=True, check=True)
    calendar = json.loads(result.stdout)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    # Preserve Sunday-to-Saturday rows, including the partial first/last weeks.
    days = [{"date": "", "contributionCount": 0, "contributionLevel": "NONE"} for _ in range(COLS * ROWS)]
    weeks = calendar["weeks"][-COLS:]
    for col, week in enumerate(weeks, COLS - len(weeks)):
        for day in week["contributionDays"]:
            days[col * ROWS + day["weekday"]] = day
    return days, calendar["totalContributions"]


def fmt(n):
    return f"{n:.3f}".rstrip("0").rstrip(".") or "0"


def animate(attribute, times, values, *, kind="animate", easing=False, extra=""):
    attrs = f'attributeName="{attribute}" dur="{CYCLE}s" repeatCount="indefinite" '
    attrs += f'keyTimes="{";".join(f"{t / CYCLE:.6f}" for t in times)}" '
    attrs += f'values="{";".join(map(str, values))}"'
    if easing:
        curves = [EASE if (a, b) in [(3, 6), (21, 24)] else "0 0 1 1"
                  for a, b in zip(times, times[1:])]
        attrs += f' calcMode="spline" keySplines="{";".join(curves)}"'
    return f'<{kind} {attrs} {extra}/>'


def simplify(times, values, tolerance):
    """Keep the motion within a subpixel/opacity bound without redundant holds."""
    keep = {0, len(times) - 1}

    def split(start, end):
        worst, at = 0, None
        for i in range(start + 1, end):
            u = (times[i] - times[start]) / (times[end] - times[start])
            error = max(abs(values[i][axis] - (a + (b - a) * u))
                        for axis, (a, b) in enumerate(zip(values[start], values[end])))
            if error > worst:
                worst, at = error, i
        if worst > tolerance:
            keep.add(at)
            split(start, at)
            split(at, end)

    split(0, len(times) - 1)
    indices = sorted(keep)
    return [times[i] for i in indices], [values[i] for i in indices]


def build_svg(days, total, motion):
    assert len(days) == 371 and all(len(frame) == 371 for frame in motion["frames"])
    gx = (WIDTH - ((COLS - 1) * PITCH + CELL)) / 2 + CELL / 2
    gy = 200 - (ROWS - 1) * PITCH / 2
    grid = [(gx + (i // ROWS) * PITCH, gy + (i % ROWS) * PITCH) for i in range(371)]
    times, frames = motion["times"], motion["frames"]
    glyph_size = motion["pitch"] * 0.94
    o = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
<title id="title">A year of contributions, a whale in motion</title>
<desc id="desc">The contribution calendar gathers into a top-down text blue whale. Its head dives first, its flukes lift and follow under water, then its nose surfaces before the body returns to the calendar. Motion is baked from dsh-ascii-whales {motion['revision']}. {total} contributions in the last year.</desc>
<style>
.m{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
.glyph{{font-family:"PingFang SC","Microsoft YaHei","Noto Sans CJK SC",sans-serif;text-anchor:middle;dominant-baseline:central}}
.still{{display:none}}
@media(prefers-reduced-motion:reduce){{.motion{{display:none}}.still{{display:inline}}}}
</style>
<rect x="8" y="8" width="884" height="384" rx="10" fill="#0d1117" stroke="#30363d"/>
<path d="M18 8H882Q892 8 892 18V42H8V18Q8 8 18 8Z" fill="#161b22"/>
<path d="M8 42H892" stroke="#30363d"/>
<circle cx="28" cy="25" r="4.5" fill="#ff5f57"/><circle cx="43" cy="25" r="4.5" fill="#febc2e"/><circle cx="58" cy="25" r="4.5" fill="#28c840"/>
<text class="m" x="450" y="29" text-anchor="middle" font-size="11" fill="#8b949e">jryang1997@github: ~ — contributions.log</text>
<g class="still">''']
    for (x, y), day in zip(grid, days):
        color = GREEN[LEVELS.index(day["contributionLevel"])]
        o.append(f'<rect x="{fmt(x - CELL / 2)}" y="{fmt(y - CELL / 2)}" width="10" height="10" rx="2" fill="{color}"/>')
    o.append('</g><g class="motion">')
    # Water is an overhead surface. Local ripples replace the old side-view waterline.
    for start, x, y in [(9.8, 658, 200), (11.0, 238, 200), (15.1, 650, 200), (17.0, 575, 200)]:
        for lag in [0, 0.5]:
            a = start + lag
            ts = [0, a, a + 0.3, a + 1.4, a + 2.1, CYCLE]
            o.append(f'<ellipse cx="{x}" cy="{y}" rx="10" ry="4" fill="none" stroke="#6e9cbd" stroke-width="0.8" opacity="0">')
            o.append(animate("rx", ts, [10, 10, 18, 46, 62, 62]))
            o.append(animate("ry", ts, [4, 4, 7, 18, 24, 24]))
            o.append(animate("opacity", ts, [0, 0, 0.3, 0.1, 0, 0]))
            o.append('</ellipse>')
    for i, ((sx, sy), day) in enumerate(zip(grid, days)):
        color = GREEN[LEVELS.index(day["contributionLevel"])]
        path = [[f[i][0], f[i][1]] for f in frames]
        pt, pv = simplify(times, path, 0.18)
        pt = [0, 3] + pt + [24, CYCLE]
        pv = [[sx, sy], [sx, sy]] + pv + [[sx, sy], [sx, sy]]
        # Shared anchors carry both the original contribution tile and its text glyph.
        o.append(f'<g transform="translate({fmt(sx)} {fmt(sy)})" opacity="1">')
        o.append(f'<title>{escape(day["date"] or "Outside the contribution period")}: {day["contributionCount"]} contributions</title>')
        o.append(animate("transform", pt, [f'{fmt(x)} {fmt(y)}' for x, y in pv],
                         kind="animateTransform", easing=True, extra='type="translate"'))
        vt, vv = simplify(times, [[f[i][2]] for f in frames], 0.012)
        o.append(animate("opacity", [0, 3] + vt + [24, CYCLE], [1, 1] + [fmt(v[0]) for v in vv] + [1, 1]))
        o.append(f'<rect x="-5" y="-5" width="10" height="10" rx="2" fill="{color}" opacity="1">')
        o.append(animate("opacity", [0, 3, 6, 21, 24, CYCLE], [1, 1, 0, 0, 1, 1], easing=True))
        o.append('</rect>')
        # The original text source and original relief tone keep the reference's character.
        light = frames[0][i][3]
        shade = round(150 + (1 - light) * 100)
        ink = f'rgb({shade - 30},{shade - 12},{min(255, shade + 12)})'
        o.append(f'<text class="glyph" font-size="{fmt(glyph_size)}" fill="{ink}" opacity="0">{"探索未至之境"[i % 6]}')
        o.append(animate("opacity", [0, 3, 6, 21, 24, CYCLE], [0, 0, 1, 1, 0, 0], easing=True))
        o.append('</text></g>')
    o.append(f'''</g>
<path d="M18 350H882" stroke="#30363d"/>
<text class="m" x="24" y="375" font-size="10" fill="#8b949e">{total:,} contributions · last 12 months</text>
<text class="m" x="876" y="375" text-anchor="end" font-size="10" fill="#6e7681">a year, in motion</text>
</svg>''')
    return "\n".join(o)


def build_static(svg):
    namespace = "http://www.w3.org/2000/svg"
    ET.register_namespace("", namespace)
    root = ET.fromstring(svg)
    for child in list(root):
        if child.get("class") == "motion":
            root.remove(child)
        elif child.get("class") == "still":
            child.set("style", "display:inline")
    root.find(f"{{{namespace}}}title").text = "Contributions in the last year"
    root.find(f"{{{namespace}}}desc").text = "Static contribution calendar for reduced motion."
    return ET.tostring(root, encoding="unicode")


def main():
    days, total = fetch_days()
    motion = json.loads((ROOT / "assets/whale-motion.json").read_text())
    svg = build_svg(days, total, motion)
    output = ROOT / "assets/contrib-ocean.svg"
    output.write_text(svg, encoding="utf-8")
    (ROOT / "assets/contrib-static.svg").write_text(build_static(svg), encoding="utf-8")
    print(f"Wrote {output}: {len(svg.encode()):,} bytes; {total:,} contributions; {len(motion['frames'])} source poses")


if __name__ == "__main__":
    main()

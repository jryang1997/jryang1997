#!/usr/bin/env python3
"""Build the terminal-style profile header SVG.

The ASCII art is derived from a CC0 sheep silhouette
(commons.wikimedia.org / LadyofHats). Re-run daily by GitHub Actions
so the star counts stay current.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import urllib.error
import urllib.request
from html import escape
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC_IMAGE = ROOT / "assets" / "sheep-source.png"
OUT_SVG = ROOT / "assets" / "header.svg"

USER = "jryang1997"
FLAGSHIP = "MenuBarMijia"

# ---- typography -----------------------------------------------------------
COLS = 62
FS = 9.4
CW = FS * 0.618
LH = 9.7
ART_X, ART_Y = 28, 86

RAMP = " .:-=+*#%@"


def sheep_ascii() -> list[str]:
    """Trace the silhouette, thicken the outline, downsample to characters."""
    im = Image.open(SRC_IMAGE).convert("RGBA")
    flat = Image.new("RGBA", im.size, (255, 255, 255, 255))
    im = Image.alpha_composite(flat, im).convert("L")

    crop = ImageOps.expand(im.crop((12, 22, 498, 700)), border=20, fill=255)
    binary = crop.point(lambda p: 0 if p < 128 else 255)
    edges = binary.filter(ImageFilter.FIND_EDGES).point(lambda p: 255 if p > 40 else 0)
    edges = ImageOps.invert(edges).filter(ImageFilter.MinFilter(13))

    draw = ImageDraw.Draw(edges)
    w, h = edges.size
    m = 18
    draw.rectangle([0, 0, w, m], fill=255)
    draw.rectangle([0, h - m, w, h], fill=255)
    draw.rectangle([0, 0, m, h], fill=255)
    draw.rectangle([w - m, 0, w, h], fill=255)

    rows = int(COLS * (crop.height / crop.width) * 0.618)
    small = edges.resize((COLS, rows), Image.LANCZOS)
    px = np.asarray(small).astype(np.float64)
    return [
        "".join(RAMP[int((255 - px[y, x]) / 255 * (len(RAMP) - 1))] for x in range(COLS))
        for y in range(rows)
    ]


def github_stats() -> tuple[int, int, int]:
    """Return (flagship stars, total stars, public repo count); 0s on failure."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        return 0, 0, 0

    def call(path: str):
        req = urllib.request.Request(
            f"https://api.github.com{path}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": f"{USER}-profile-header",
            },
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)

    try:
        repos, page = [], 1
        while True:
            batch = call(f"/users/{USER}/repos?per_page=100&page={page}&sort=pushed")
            if not batch:
                break
            repos.extend(batch)
            page += 1
            if page > 5:
                break
        owned = [r for r in repos if not r.get("fork")]
        flagship = next((r["stargazers_count"] for r in owned if r["name"] == FLAGSHIP), 0)
        total = sum(r["stargazers_count"] for r in owned)
        return flagship, total, len(owned)
    except (urllib.error.URLError, KeyError, ValueError):
        return 0, 0, 0


def build_svg(art: list[str], flagship: int, total: int, repos: int, updated: str) -> str:
    rows = len(art)
    art_w, art_h = COLS * CW, rows * LH
    ix = int(ART_X + art_w + 46)
    win_w = int(ix + 296 - 8)
    win_h = int(max(ART_Y + art_h + 44, 560))
    w, h = win_w + 16, win_h + 16
    wx = wy = 8
    top = 34

    info = [
        ("os", "macOS · Windows · Android"),
        ("role", "vibe coder · 非科班"),
        ("stack", "Swift · TS · Rust · Python"),
        ("now", f"{FLAGSHIP} · ★{flagship}"),
        ("side", "ASCII whales · AI agents"),
        ("motto", "小摩擦，搓成小工具"),
    ]

    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" '
        f'aria-label="{escape(USER)} — ASCII line-art of a ewe and her lamb, framed as a terminal window">',
        "<style>"
        ":root{--bg:#0d1117;--bar:#161b22;--bd:#30363d;--fg:#e6edf3;--mu:#8b949e;"
        "--am:#e3b341;--gr:#7ee787;--sav:#6e7681;--art:#9fb0c0;}"
        '.m{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace}'
        "</style>",
        f'<rect x="{wx}" y="{wy}" width="{win_w}" height="{win_h}" rx="10" '
        f'fill="var(--bg)" stroke="var(--bd)" stroke-width="1.5"/>',
        f'<path d="M{wx+10} {wy} h{win_w-20} a10,10 0 0 1 10,10 v{top-10} h-{win_w} '
        f'v-{top-10} a10,10 0 0 1 10,-10 z" fill="var(--bar)"/>',
        f'<path d="M{wx+10} {wy+top} H{wx+win_w-10}" stroke="var(--bd)" stroke-width="1"/>',
    ]
    for i, colour in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        o.append(
            f'<circle cx="{wx+20+i*15}" cy="{wy+16}" r="4.5" fill="{colour}" opacity="0.9"/>'
        )
    o.append(
        f'<text class="m" x="{wx+win_w/2}" y="{wy+20}" text-anchor="middle" '
        f'font-size="11" fill="var(--mu)">{escape(USER)}@github: ~ — sheep.txt</text>'
    )

    o.append(
        '<g font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
        f'font-size="{FS}" fill="var(--art)">'
    )
    for i, line in enumerate(art):
        if line.strip():
            o.append(
                f'<text x="{ART_X}" y="{ART_Y+i*LH:.1f}" xml:space="preserve">{escape(line)}</text>'
            )
    o.append("</g>")

    y = ART_Y + 46
    o.append(f'<text class="m" x="{ix}" y="{y}" font-size="11" fill="var(--sav)"># 母羊和她的小羊</text>')
    y += 28
    o.append(
        f'<text class="m" x="{ix}" y="{y}" font-size="15" fill="var(--fg)" '
        f'font-weight="600">一只羊的 ASCII</text>'
    )
    y += 30
    for key, value in info:
        o.append(f'<text class="m" x="{ix}" y="{y}" font-size="11" fill="var(--am)">{escape(key)}</text>')
        o.append(
            f'<text class="m" x="{ix+48}" y="{y}" font-size="11" fill="var(--fg)" '
            f'xml:space="preserve">{escape(value)}</text>'
        )
        y += 22
    y += 6
    o.append(f'<text class="m" x="{ix}" y="{y}" font-size="11" fill="var(--sav)">$</text>')
    o.append(
        f'<rect x="{ix+9}" y="{y-9}" width="6" height="11" fill="var(--gr)" opacity="0.8">'
        '<animate attributeName="opacity" values="0.8;0;0.8" dur="1.15s" repeatCount="indefinite"/>'
        "</rect>"
    )

    status_y = win_h - 8
    o.append(f'<path d="M{wx+10} {status_y-20} H{wx+win_w-10}" stroke="var(--bd)" stroke-width="1"/>')
    o.append(
        f'<text class="m" x="{wx+14}" y="{status_y-4}" font-size="10" fill="var(--mu)" '
        f'xml:space="preserve">[0] 0:zsh*  sheep.txt — {COLS}×{rows}</text>'
    )
    o.append(
        f'<text class="m" x="{wx+win_w/2}" y="{status_y-4}" font-size="10" fill="var(--sav)" '
        f'text-anchor="middle">{total}★ · {repos} repos</text>'
    )
    o.append(
        f'<text class="m" x="{wx+win_w-14}" y="{status_y-4}" font-size="10" fill="var(--mu)" '
        f'text-anchor="end">updated {escape(updated)}</text>'
    )
    o.append("</svg>")
    return "\n".join(o)


def main() -> None:
    art = sheep_ascii()
    flagship, total, repos = github_stats()
    updated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    OUT_SVG.write_text(build_svg(art, flagship, total, repos, updated), encoding="utf-8")
    print(f"wrote {OUT_SVG.relative_to(ROOT)} — {COLS}x{len(art)}, ★{total} across {repos} repos")


if __name__ == "__main__":
    main()

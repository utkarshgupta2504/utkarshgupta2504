#!/usr/bin/env python3
"""Builds the animated SVGs in ../assets that the profile README shows.

Everything the cards say lives in this file. Edit the data below, then:

    python3 -m venv .venv && .venv/bin/pip install fonttools brotli
    .venv/bin/python scripts/build.py

Curvet's own fonts (Outfit for display, Inter for text) are subset to the
characters each SVG uses and embedded, because GitHub serves README images
with external loads blocked. Text is measured with the same fonts, so chips
and pills size themselves.
"""

import base64
import io
import re
from html import escape, unescape
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
FONTS = {"Outfit": ROOT / "scripts/fonts/Outfit.woff2", "Inter": ROOT / "scripts/fonts/Inter.woff2"}
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

# Curvet palette (darkapp-haven: index.css + tailwind.config.ts)
BG = "#09090b"
CARD = "#0c0c0f"
CHIP = "#18181b"
BORDER = "#27272a"
TEXT = "#fafafa"
SOFT = "#e4e4e7"
MUTED = "#a1a1aa"
DIM = "#71717a"
FAINT = "#52525b"
PURPLE = "#8B5CF6"
VIOLET = "#a78bfa"
BLUE = "#4F46E5"
SKY = "#0EA5E9"
PINK = "#DB2777"
GREEN = "#6DCA91"
RED = "#f87171"

# Light tints of the brand gradient, for text on black.
BRAND_STOPS = [(0, "#f9a8d4"), (0.35, "#c4b5fd"), (0.7, "#a5b4fc"), (1, "#7dd3fc")]


# ---------------------------------------------------------------- fonts

_metrics = {}


def _font_at(name, wght):
    key = (name, wght)
    if key not in _metrics:
        font = instantiateVariableFont(TTFont(FONTS[name]), {"wght": wght})
        _metrics[key] = (font.getBestCmap(), font["hmtx"], font["head"].unitsPerEm)
    return _metrics[key]


def tw(text, size, font="Inter", wght=400, ls=0.0):
    """Rendered width of text in px (no kerning; close enough for layout)."""
    cmap, hmtx, upm = _font_at(font, wght)
    units = sum(hmtx[cmap[ord(c)]][0] if ord(c) in cmap else upm * 0.6 for c in text)
    return units * size / upm + ls * len(text)


def wrap(text, width, size, font="Inter", wght=400):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if line and tw(trial, size, font, wght) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + [line]


def _embedded_fonts(svg):
    chars = set()
    for body in re.findall(r"<text[^>]*>(.*?)</text>", svg, re.S):
        chars |= set(unescape(re.sub(r"<[^>]+>", "", body)))
    chars |= set(" ")
    faces = []
    for name, path in FONTS.items():
        if f'class="{name[0].lower()}' not in svg:
            continue
        font = TTFont(path)
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = ["kern", "liga", "calt", "tnum", "ss01", "cv11"]
        sub = subset.Subsetter(opts)
        sub.populate(unicodes=[ord(c) for c in chars])
        sub.subset(font)
        buf = io.BytesIO()
        font.flavor = "woff2"
        font.save(buf)
        data = base64.b64encode(buf.getvalue()).decode()
        faces.append(
            f"@font-face{{font-family:{name};font-weight:100 900;"
            f"src:url(data:font/woff2;base64,{data}) format('woff2')}}"
        )
    return "".join(faces)


def svg_doc(w, h, body, css="", label=""):
    base = (
        f".o{{font-family:Outfit,Inter,system-ui,sans-serif}}"
        f".i{{font-family:Inter,system-ui,sans-serif;letter-spacing:-.011em}}"
        f".m{{font-family:{MONO}}}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
    )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" role="img" aria-label="{escape(label)}">'
        f"<title>{escape(label)}</title>"
        f"<style>{{FONTS}}{base}{css}</style>{body}</svg>"
    )
    return svg.replace("{FONTS}", _embedded_fonts(svg))


# ---------------------------------------------------------------- shared bits

MARK = re.search(r"<path d=\"([^\"]+)\"", (ROOT / "scripts/brand/curvet-mark.svg").read_text()).group(1)
LOGO_PATHS = re.findall(r"<path d=\"([^\"]+)\"", (ROOT / "scripts/brand/curvet-logo.svg").read_text())


def grad(gid, stops=BRAND_STOPS, x2=1, y2=0, units=""):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    u = f' gradientUnits="userSpaceOnUse"' if units else ""
    extra = units if units else f'x1="0" y1="0" x2="{x2}" y2="{y2}"'
    return f'<linearGradient id="{gid}" {extra}{u}>{s}</linearGradient>'


def t(x, y, text, size, cls="i", fill=TEXT, wght=400, anchor="start", extra=""):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" font-size="{size}" font-weight="{wght}" '
        f'fill="{fill}"{a} {extra}>{escape(text)}</text>'
    )


def card_bg(w, h, rx=20, fill=CARD):
    return (
        f'<rect width="{w}" height="{h}" rx="{rx}" fill="{fill}"/>'
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{rx - .5}" stroke="{BORDER}"/>'
    )


def blur_filter(fid, sd):
    return f'<filter id="{fid}" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="{sd}"/></filter>'


GRAIN = (
    '<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" '
    'stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter>'
)


def write(name, svg):
    (OUT / name).write_text(svg)
    print(f"  {name:<28} {len(svg) / 1024:6.1f} KB")


# ---------------------------------------------------------------- hero

def hero():
    W, H = 840, 300
    phrases = [
        "AI products, end to end",
        "model routers that fall back",
        "agent runtimes",
        "the apps people actually use",
    ]
    cycle = 3.2 * len(phrases)
    pill = "Co-Founder & CTO · curvet.ai"
    pill_w = tw(pill, 13, wght=500) + 46
    lead = "I build "
    lead_x = 48 + tw(lead, 21)

    rot = ""
    for i, p in enumerate(phrases):
        rot += t(lead_x, 176, p, 21, "i rot", "url(#brand)", 500,
                 extra=f'style="animation-delay:{i * 3.2}s"')
    meta = [("Bengaluru, India",), ("ex-Samsung R&D",), ("NSUT ’23",), ("utkarshgupta.dev",)]
    spans = f'<tspan fill="{FAINT}">  ·  </tspan>'.join(f"<tspan>{escape(m[0])}</tspan>" for m in meta)

    css = (
        f".rot{{opacity:0;animation:rot {cycle}s infinite}}"
        "@keyframes rot{0%{opacity:0;transform:translateY(10px)}3%{opacity:1;transform:none}"
        f"{100 / len(phrases) - 3:.1f}%{{opacity:1;transform:none}}"
        f"{100 / len(phrases):.1f}%{{opacity:0;transform:translateY(-10px)}}100%{{opacity:0}}}}"
        "@media (prefers-reduced-motion:reduce){.rot:first-of-type{opacity:1}}"
        ".b1{animation:d1 15s ease-in-out infinite alternate}"
        ".b2{animation:d2 18s ease-in-out infinite alternate}"
        ".b3{animation:d3 13s ease-in-out infinite alternate}"
        ".b4{animation:d2 21s ease-in-out infinite alternate-reverse}"
        "@keyframes d1{to{transform:translate(-90px,50px)}}"
        "@keyframes d2{to{transform:translate(-60px,-70px)}}"
        "@keyframes d3{to{transform:translate(110px,-40px)}}"
        ".float{animation:fl 7s ease-in-out infinite}"
        "@keyframes fl{50%{transform:translateY(-8px)}}"
        ".up{animation:up .9s cubic-bezier(.2,.7,.2,1) backwards}"
        "@keyframes up{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}"
    )
    body = f"""
<defs>
  <clipPath id="clip"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  {blur_filter("blur", 52)}{GRAIN}
  {grad("brand")}
  {grad("markfill", [(0, "#ffffff"), (1, "#c4b5fd")], 1, 1)}
  {grad("name", [(0, "#ffffff"), (1, "#d4d4d8")], 0, 1)}
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#fff" fill-opacity=".08"/></pattern>
  <radialGradient id="fade" cx=".78" cy=".45" r=".6"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>
  <mask id="dotmask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
</defs>
<g clip-path="url(#clip)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <g filter="url(#blur)" opacity=".6">
    <circle class="b1" cx="670" cy="70" r="125" fill="{PURPLE}"/>
    <circle class="b2" cx="800" cy="250" r="115" fill="{SKY}"/>
    <circle class="b3" cx="520" cy="300" r="95" fill="{PINK}"/>
    <circle class="b4" cx="830" cy="40" r="85" fill="{BLUE}"/>
  </g>
  <rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#dotmask)"/>
  <rect width="{W}" height="{H}" filter="url(#grain)" opacity=".06"/>
  <g transform="translate(618 52) scale(1.55)"><g class="float"><path d="{MARK}" fill="url(#markfill)"/></g></g>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="21.5" stroke="#ffffff" stroke-opacity=".08"/>

<g class="up" style="animation-delay:.05s">
  <rect x="48" y="38" width="{pill_w:.1f}" height="30" rx="15" fill="#ffffff" fill-opacity=".05" stroke="#ffffff" stroke-opacity=".12"/>
  <circle cx="64" cy="53" r="3.5" fill="{GREEN}"/>
  <circle cx="64" cy="53" r="3.5" fill="none" stroke="{GREEN}">
    <animate attributeName="r" values="3.5;9" dur="2s" repeatCount="indefinite"/>
    <animate attributeName="stroke-opacity" values=".8;0" dur="2s" repeatCount="indefinite"/>
  </circle>
  {t(77, 57.5, pill, 13, fill=SOFT, wght=500)}
</g>
<g class="up" style="animation-delay:.15s">{t(45, 132, "Utkarsh Gupta", 60, "o", "url(#name)", 600, extra='letter-spacing="-1.5"')}</g>
<g class="up" style="animation-delay:.3s">{t(48, 176, lead, 21, fill=MUTED)}{rot}</g>
<g class="up" style="animation-delay:.45s"><text x="48" y="248" class="i" font-size="13.5" fill="{DIM}">{spans}</text></g>
"""
    write("hero.svg", svg_doc(W, H, body, css, "Utkarsh Gupta, Co-Founder and CTO of Curvet"))


# ---------------------------------------------------------------- stats

def stats():
    W, H, gap = 840, 112, 12
    items = [
        ("100+", "AI models behind one API"),
        ("28", "providers integrated"),
        ("3", "npm packages shipped"),
        ("10M+", "Galaxy users, at Samsung"),
    ]
    tile = (W - gap * (len(items) - 1)) / len(items)
    body = f"<defs>{grad('num', units=f'x1=\"0\" y1=\"0\" x2=\"{W}\" y2=\"0\"')}{grad('edge', [(0, '#ffffff00'), (.5, '#ffffff40'), (1, '#ffffff00')])}</defs>"
    for i, (num, label) in enumerate(items):
        x = i * (tile + gap)
        size = 13
        while tw(label, size) > tile - 44:
            size -= 0.5
        body += f"""
<g class="up" style="animation-delay:{.08 + i * .1:.2f}s">
  <rect x="{x:.1f}" y="0" width="{tile:.1f}" height="{H}" rx="16" fill="{CARD}"/>
  <rect x="{x + .5:.1f}" y=".5" width="{tile - 1:.1f}" height="{H - 1}" rx="15.5" stroke="{BORDER}"/>
  <rect x="{x + 24:.1f}" y="0" width="{tile - 48:.1f}" height="1" fill="url(#edge)"/>
  {t(x + 22, 58, num, 38, "o", "url(#num)", 600, extra='letter-spacing="-1"')}
  {t(x + 22, 86, label, size, fill=MUTED)}
</g>"""
    css = (
        ".up{animation:up .8s cubic-bezier(.2,.7,.2,1) backwards}"
        "@keyframes up{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}"
    )
    write("stats.svg", svg_doc(W, H, body, css, "100+ models, 28 providers, 3 npm packages, 10M+ users"))


# ---------------------------------------------------------------- auto router

def router():
    W, H, D = 840, 372, 7.0  # D = loop length in seconds
    app = (32, 156, 222, 100)
    rt = (322, 142, 210, 128)
    cy = rt[1] + rt[3] / 2
    providers = ["Google · Gemini", "Anthropic · Claude", "OpenAI · GPT", "Alibaba · Qwen", "DeepInfra · open models"]
    px, pw, ph = 616, 192, 32
    pys = [cy - 88 + i * 44 for i in range(len(providers))]
    FAIL, OK = 0, 1

    def k(s):
        return f"{s / D:.4f}"

    def motion(pid, t0, t1, rev=False):
        kp = "1;1;0;0" if rev else "0;0;1;1"
        return (
            f'<animateMotion dur="{D}s" repeatCount="indefinite" calcMode="linear" '
            f'keyPoints="{kp}" keyTimes="0;{k(t0)};{k(t1)};1"><mpath xlink:href="#{pid}"/></animateMotion>'
        )

    def window(attr, t0, t1, on="1", off="0"):
        return (
            f'<animate attributeName="{attr}" dur="{D}s" repeatCount="indefinite" calcMode="discrete" '
            f'values="{off};{on};{off}" keyTimes="0;{k(t0)};{k(t1)}"/>'
        )

    def packet(pid, t0, t1, color="#fff", rev=False):
        return (
            f'<g opacity="0">{window("opacity", t0, t1)}{motion(pid, t0, t1, rev)}'
            f'<circle r="9" fill="{color}" opacity=".35" filter="url(#glow)"/><circle r="3.6" fill="{color}"/></g>'
        )

    ax, ay, aw, ah = app
    paths = f'<path id="pin" d="M{ax + aw} {cy} H{rt[0]}"/>'
    for i, y in enumerate(pys):
        sx = rt[0] + rt[2]
        paths += f'<path id="p{i}" d="M{sx} {cy} C{sx + 50} {cy} {px - 50} {y} {px} {y}"/>'

    body = f"""
<defs>
  {blur_filter("glow", 5)}{blur_filter("soft", 60)}
  {grad("brand")}
  {grad("rtedge", [(0, PURPLE), (.5, BLUE), (1, SKY)], 1, 1)}
  {paths}
</defs>
{card_bg(W, H, 22, BG)}
<g filter="url(#soft)" opacity=".28"><circle cx="420" cy="210" r="120" fill="{PURPLE}"/><circle cx="720" cy="190" r="90" fill="{SKY}"/></g>
{t(32, 46, "Inside the auto router", 20, "o", TEXT, 600, extra='letter-spacing="-.3"')}
{t(32, 70, "What happens when an app calls Curvet with model: \"auto\" and the first pick is busy.", 13.5, fill=DIM)}

<use xlink:href="#pin" stroke="{BORDER}" stroke-width="1.5"/>
"""
    for i in range(len(providers)):
        stroke = f'<use xlink:href="#p{i}" stroke="{BORDER}" stroke-width="1.5"/>'
        if i == FAIL:
            stroke += f'<use xlink:href="#p{i}" stroke="{RED}" stroke-width="1.5" opacity="0">{window("opacity", 2.3, 3.2, ".8")}</use>'
        if i == OK:
            stroke += f'<use xlink:href="#p{i}" stroke="{GREEN}" stroke-width="1.5" opacity="0">{window("opacity", 3.3, 6.4, ".7")}</use>'
        body += stroke

    # the app
    body += f"""
<rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" rx="14" fill="{CARD}" stroke="{BORDER}"/>
{t(ax + 18, ay + 26, "YOUR APP", 10.5, fill=DIM, wght=600, extra='letter-spacing="1.4"')}
{t(ax + 18, ay + 52, "POST /v1/chat/completions", 11.5, "m", SOFT)}
{t(ax + 18, ay + 74, 'model: "auto"', 11.5, "m", VIOLET)}
<g opacity="0">{window("opacity", 4.9, 6.6)}
  <rect x="{ax}" y="{ay + ah + 10}" width="{aw}" height="28" rx="14" fill="{GREEN}" fill-opacity=".1" stroke="{GREEN}" stroke-opacity=".35"/>
  {t(ax + aw / 2, ay + ah + 28.5, "✓ 200 · fell back once", 12, fill=GREEN, wght=500, anchor="middle")}
</g>
"""
    # the router
    rx_, ry_, rw_, rh_ = rt
    bars = [("quality", .86, .74), ("price", .62, .70), ("health", .95, .08)]
    bar_rows = ""
    for j, (name, a, b) in enumerate(bars):
        by = ry_ + 72 + j * 18
        bar_rows += t(rx_ + 20, by + 4, name, 11, fill=DIM)
        bar_rows += f'<rect x="{rx_ + 76}" y="{by - 2}" width="{rw_ - 96}" height="5" rx="2.5" fill="{CHIP}"/>'
        # first pick's scores, then the fallback's once the first pick is marked unhealthy
        full = rw_ - 96
        bar_rows += (
            f'<rect x="{rx_ + 76}" y="{by - 2}" width="0" height="5" rx="2.5" fill="url(#rtedge)">'
            f'<animate attributeName="width" dur="{D}s" repeatCount="indefinite" '
            f'values="0;0;{full * a:.1f};{full * a:.1f};{full * (b if name == "health" else a):.1f};{full * (b if name == "health" else a):.1f};0" '
            f'keyTimes="0;{k(1.1)};{k(1.5)};{k(2.3)};{k(2.5)};{k(6.6)};1"/></rect>'
        )
    body += f"""
<rect x="{rx_}" y="{ry_}" width="{rw_}" height="{rh_}" rx="16" fill="{CARD}"/>
<rect x="{rx_ + .5}" y="{ry_ + .5}" width="{rw_ - 1}" height="{rh_ - 1}" rx="15.5" stroke="url(#rtedge)" stroke-opacity=".55"/>
<rect x="{rx_ - 3}" y="{ry_ - 3}" width="{rw_ + 6}" height="{rh_ + 6}" rx="19" stroke="{VIOLET}" stroke-width="2" opacity="0">
  <animate attributeName="opacity" dur="{D}s" repeatCount="indefinite" values="0;0;.9;0;0;.9;0;0" keyTimes="0;{k(1.1)};{k(1.2)};{k(1.6)};{k(2.35)};{k(2.45)};{k(2.9)};1"/>
</rect>
<g transform="translate({rx_ + 18} {ry_ + 16}) scale(.2)"><path d="{MARK}" fill="#fff"/></g>
{t(rx_ + 50, ry_ + 36, "auto", 17, "o", TEXT, 600)}
{t(rx_ + 50 + tw("auto ", 17, "Outfit", 600), ry_ + 36, "router", 17, "o", MUTED, 400)}
{bar_rows}
"""
    # providers
    for i, (name, y) in enumerate(zip(providers, pys)):
        body += (
            f'<rect x="{px}" y="{y - ph / 2}" width="{pw}" height="{ph}" rx="10" fill="{CARD}" stroke="{BORDER}"/>'
            f'<circle cx="{px + 16}" cy="{y}" r="3.5" fill="{FAINT}">'
        )
        if i == FAIL:
            body += f'<animate attributeName="fill" dur="{D}s" repeatCount="indefinite" calcMode="discrete" values="{FAINT};{RED};{FAINT}" keyTimes="0;{k(2.3)};{k(6.6)}"/>'
        if i == OK:
            body += f'<animate attributeName="fill" dur="{D}s" repeatCount="indefinite" calcMode="discrete" values="{FAINT};{GREEN};{FAINT}" keyTimes="0;{k(3.3)};{k(6.6)}"/>'
        body += "</circle>" + t(px + 28, y + 4.5, name, 12.5, fill=SOFT)
        if i == FAIL:
            body += f'<g opacity="0">{window("opacity", 2.3, 6.6)}{t(px + pw - 14, y + 4.5, "429", 11.5, "m", RED, 600, "end")}</g>'
        if i == OK:
            body += f'<g opacity="0">{window("opacity", 3.3, 6.6)}{t(px + pw - 14, y + 4.5, "200", 11.5, "m", GREEN, 600, "end")}</g>'

    body += packet("pin", .3, 1.1)
    body += packet(f"p{FAIL}", 1.6, 2.3)
    body += packet(f"p{OK}", 2.6, 3.3)
    body += packet(f"p{OK}", 3.5, 4.2, GREEN, rev=True)
    body += packet("pin", 4.2, 4.9, GREEN, rev=True)
    body += t(W / 2, H - 26, "one key  ·  one balance  ·  100+ models from 28 providers  ·  fallback across providers", 12.5, fill=DIM, anchor="middle")
    write("router.svg", svg_doc(W, H, body, "", "Animated diagram: Curvet's auto router scoring models and falling back across providers"))


# ---------------------------------------------------------------- terminal

def terminal():
    W, size, step, x0, y0 = 840, 14, 26, 30, 82
    cw = size * 0.6
    lines = [
        ("cmd", "npm i -g @curvet/cli"),
        ("dim", "added 1 package in 2s"),
        ("cmd", 'curvet chat -m auto "who is utkarsh?"'),
        ("note", "▸ auto picked a model · streaming"),
        ("out", "Co-founder & CTO of Curvet. Built it from zero: 100+ models behind"),
        ("out", "one API key, a workflow engine that runs the same code in the browser"),
        ("out", "and on the server, and an agent runtime with tiered, search-loaded tools."),
        ("out", "Before that: Senior SWE at Samsung R&D, shipping to 10M+ Galaxy users."),
        ("ok", "✓ done · 1 request · 0 errors"),
        ("prompt", ""),
    ]
    H = y0 + step * len(lines) + 4
    colors = {"dim": DIM, "note": VIOLET, "out": SOFT, "ok": GREEN}

    # events: (time, line, revealed chars) ; cursor follows the same events
    events, now = [], 0.6
    for i, (kind, text) in enumerate(lines):
        if kind in ("cmd", "prompt"):
            events.append((now, i, 2))  # "$ "
            if kind == "prompt":
                break
            now += 0.35
            for c in range(1, len(text) + 1):
                now += 0.045
                events.append((now, i, 2 + c))
            now += 0.45
        elif kind == "out":
            for m in re.finditer(r"\S+\s*", text):
                now += 0.05
                events.append((now, i, m.end()))
            now += 0.05
        else:
            now += 0.25
            events.append((now, i, len(text)))
    D = now + 4.5

    def k(s):
        return f"{s / D:.4f}"

    body = f"""
<defs>{blur_filter("soft", 70)}</defs>
{card_bg(W, H, 18, BG)}
<g filter="url(#soft)" opacity=".18"><circle cx="760" cy="{H}" r="120" fill="{PURPLE}"/><circle cx="640" cy="{H + 40}" r="90" fill="{SKY}"/></g>
<path d="M18 1H{W - 18}A17 17 0 0 1 {W - 1} 18V44H1V18A17 17 0 0 1 18 1Z" fill="#ffffff" fill-opacity=".03"/>
<path d="M1 44.5H{W - 1}" stroke="{BORDER}"/>
<circle cx="24" cy="22.5" r="5.5" fill="#3f3f46"/><circle cx="43" cy="22.5" r="5.5" fill="#3f3f46"/><circle cx="62" cy="22.5" r="5.5" fill="#3f3f46"/>
{t(W / 2, 27, "utkarsh@curvet: ~", 12.5, "m", DIM, anchor="middle")}
"""
    for i, (kind, text) in enumerate(lines):
        y = y0 + i * step
        mine = [(ts, n) for ts, li, n in events if li == i]
        widths = ["0"] + [f"{n * cw:.1f}" for _, n in mine] + ["0"]
        times = ["0"] + [k(ts) for ts, _ in mine] + [k(D - 0.3)]
        body += (
            f'<clipPath id="c{i}"><rect x="{x0}" y="{y - 17}" height="{step}" width="0">'
            f'<animate attributeName="width" dur="{D:.2f}s" repeatCount="indefinite" calcMode="discrete" '
            f'values="{";".join(widths)}" keyTimes="{";".join(times)}"/></rect></clipPath>'
        )
        full = len(text) + (2 if kind in ("cmd", "prompt") else 0)
        tl = f'textLength="{full * cw:.1f}" lengthAdjust="spacing"' if full else ""
        if kind in ("cmd", "prompt"):
            inner = f'<tspan fill="{VIOLET}">$ </tspan><tspan fill="{TEXT}">{escape(text)}</tspan>'
            body += f'<text x="{x0}" y="{y}" class="m" font-size="{size}" {tl} xml:space="preserve" clip-path="url(#c{i})">{inner}</text>'
        else:
            body += f'<text x="{x0}" y="{y}" class="m" font-size="{size}" fill="{colors[kind]}" {tl} xml:space="preserve" clip-path="url(#c{i})">{escape(text)}</text>'

    xs = [f"{x0 + n * cw:.1f}" for _, _, n in events]
    ys = [f"{y0 + li * step - 14:.1f}" for _, li, _ in events]
    times = ["0"] + [k(ts) for ts, _, _ in events] + [k(D - 0.3)]
    body += (
        f'<rect class="cur" x="{x0}" y="{y0 - 14}" width="{cw:.1f}" height="18" rx="1.5" fill="{VIOLET}">'
        f'<animate attributeName="x" dur="{D:.2f}s" repeatCount="indefinite" calcMode="discrete" values="{x0};{";".join(xs)};{x0}" keyTimes="{";".join(times)}"/>'
        f'<animate attributeName="y" dur="{D:.2f}s" repeatCount="indefinite" calcMode="discrete" values="{y0 - 14};{";".join(ys)};{y0 - 14}" keyTimes="{";".join(times)}"/>'
        "</rect>"
    )
    css = ".cur{animation:blink 1.1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
    write("terminal.svg", svg_doc(W, H, body, css, "Terminal: asking the Curvet CLI who Utkarsh is"))


# ---------------------------------------------------------------- project cards

PROJECTS = [
    {
        "file": "card-curvet.svg",
        "kicker": "PRODUCT",
        "name": "Curvet",
        "badge": ("Live", GREEN),
        "tagline": "Every AI model, one workspace",
        "desc": "Chat, image, video, voice and 3D across 100+ models, plus visual workflows, agents, "
                "real-time collaboration and a public API. One key, one balance.",
        "chips": ["React", "TypeScript", "Node.js", "MongoDB", "GCP"],
        "glow": PURPLE,
    },
    {
        "file": "card-sdk.svg",
        "kicker": "OPEN SOURCE · NPM",
        "name": "@curvet/sdk + cli",
        "badge": ("2026", None),
        "tagline": "Curvet in your code and your terminal",
        "desc": "The official TypeScript SDK and CLI: chat, media, workflows and billing from one client. "
                "The CLI doubles as an MCP server for Claude, Cursor and friends.",
        "chips": ["TypeScript", "Node.js", "MCP"],
        "glow": SKY,
    },
    {
        "file": "card-testgen.svg",
        "kicker": "OPEN SOURCE",
        "name": "cline-testgen",
        "badge": ("2026", None),
        "tagline": "An agent that writes the tests you're missing",
        "desc": "Reads a Spring Boot class and its tests, finds the gaps, and generates the missing "
                "JUnit cases, weighted toward edge cases. Fully local on Gemma via Ollama.",
        "chips": ["Cline SDK", "Ollama", "Python", "Node.js"],
        "glow": BLUE,
    },
    {
        "file": "card-navifinder.svg",
        "kicker": "SMART INDIA HACKATHON",
        "name": "NaviFinder",
        "badge": ("2022", None),
        "tagline": "Indoor + outdoor navigation with ML",
        "desc": "Fuses phone sensors with WiFi and GPS for seamless navigation, 20% more accurate. "
                "SIH 2022 finalist on ISRO's problem statement.",
        "chips": ["React Native", "Flask", "PyTorch"],
        "glow": PINK,
    },
]


def project_card(p):
    W, H = 410, 230
    pad = 26
    body = f"""
<defs>{blur_filter("soft", 45)}{grad("tag", [(0, "#ffffff"), (1, "#c4b5fd")])}
<clipPath id="clip"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>
{card_bg(W, H, 18)}
<g clip-path="url(#clip)"><circle class="glow" cx="{W - 10}" cy="-10" r="100" fill="{p['glow']}" filter="url(#soft)"/></g>
{t(pad, 36, p["kicker"], 10.5, fill=DIM, wght=600, extra='letter-spacing="1.3"')}
"""
    label, dot = p["badge"]
    bw = tw(label, 11.5, wght=500) + (32 if dot else 20)
    bx = W - pad - bw
    body += f'<rect x="{bx:.1f}" y="20" width="{bw:.1f}" height="22" rx="11" fill="#ffffff" fill-opacity=".05" stroke="#ffffff" stroke-opacity=".1"/>'
    if dot:
        body += f'<circle cx="{bx + 13:.1f}" cy="31" r="3" fill="{dot}"><animate attributeName="opacity" values="1;.35;1" dur="2s" repeatCount="indefinite"/></circle>'
    body += t(bx + (22 if dot else 10), 35, label, 11.5, fill=SOFT, wght=500)
    body += t(pad - 1, 72, p["name"], 24, "o", TEXT, 600, extra='letter-spacing="-.5"')
    body += t(pad - 1 + tw(p["name"], 24, "Outfit", 600, -.5) + 8, 71, "↗", 17, fill=DIM)
    body += t(pad, 97, p["tagline"], 14, fill="url(#tag)", wght=500)
    for j, line in enumerate(wrap(p["desc"], W - pad * 2, 13)[:3]):
        body += t(pad, 124 + j * 19, line, 13, fill=MUTED)
    cx = pad
    for chip in p["chips"]:
        cwid = tw(chip, 11.5, wght=500) + 20
        body += (
            f'<rect x="{cx:.1f}" y="{H - 46}" width="{cwid:.1f}" height="24" rx="8" fill="{CHIP}" stroke="{BORDER}"/>'
            + t(cx + 10, H - 29.5, chip, 11.5, fill=SOFT, wght=500)
        )
        cx += cwid + 6
    css = ".glow{opacity:.32;animation:br 6s ease-in-out infinite}@keyframes br{50%{opacity:.5}}"
    write(p["file"], svg_doc(W, H, body, css, f"{p['name']}: {p['tagline']}"))


# ---------------------------------------------------------------- stack

STACK = [
    ("AI & LLM", ["LLM orchestration", "Agents & tool use", "MCP", "Model routing", "Prompt caching", "Speech (ASR / TTS)", "Ollama"]),
    ("Languages", ["TypeScript", "Python", "Dart", "Java", "C++", "SQL"]),
    ("Backend", ["Node.js", "Express", "MongoDB", "FastAPI", "Django", "Socket.io", "SSE streaming"]),
    ("Frontend & Mobile", ["React", "Vite", "Tailwind", "TanStack Query", "three.js", "Flutter", "React Native"]),
    ("Cloud & Ops", ["GCP", "AWS", "Docker", "nginx", "pm2", "OpenTelemetry", "Grafana", "PostHog"]),
]
CORE = {"Agents & tool use", "MCP", "Model routing", "TypeScript", "Node.js", "React", "GCP", "Flutter"}


def stack():
    W, pad, label_w, ch, gap, row_gap = 840, 28, 150, 30, 7, 18
    x_start, x_end = pad + label_w, W - pad
    rows, y = [], pad
    for cat, skills in STACK:
        x, chips, top = x_start, [], y
        for s in skills:
            w = tw(s, 13, wght=500) + 24 + (10 if s in CORE else 0)
            if x + w > x_end:
                x, y = x_start, y + ch + gap
            chips.append((x, y, w, s))
            x += w + gap
        rows.append((cat, top, chips))
        y += ch + row_gap
    H = y - row_gap + pad

    body = f"<defs>{grad('brand')}{grad('core', [(0, PINK), (.4, PURPLE), (1, SKY)], 1, 1)}"
    body += '<linearGradient id="shine" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".14"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
    body += '<clipPath id="chips">' + "".join(
        f'<rect x="{x:.1f}" y="{yy}" width="{w:.1f}" height="{ch}" rx="9"/>' for _, _, chips in rows for x, yy, w, _ in chips
    ) + "</clipPath></defs>"
    body += card_bg(W, H, 20)
    for i, (cat, top, chips) in enumerate(rows):
        if i:
            body += f'<path d="M{pad} {top - row_gap / 2:.1f}H{W - pad}" stroke="{BORDER}" stroke-opacity=".6"/>'
        body += f'<rect x="{pad}" y="{top + 11}" width="8" height="8" rx="2" fill="url(#core)"/>'
        body += t(pad + 18, top + 19.5, cat.upper(), 11, fill=MUTED, wght=600, extra='letter-spacing="1.1"')
        for x, yy, w, s in chips:
            core = s in CORE
            stroke = "url(#core)" if core else BORDER
            body += f'<rect x="{x + .5:.1f}" y="{yy + .5}" width="{w - 1:.1f}" height="{ch - 1}" rx="8.5" fill="{CHIP}" stroke="{stroke}" stroke-opacity="{.8 if core else 1}"/>'
            tx = x + 12
            if core:
                body += f'<circle cx="{x + 15:.1f}" cy="{yy + ch / 2}" r="2.5" fill="url(#core)"/>'
                tx += 10
            body += t(tx, yy + 19.5, s, 13, fill=TEXT if core else SOFT, wght=500)
    body += f'<g clip-path="url(#chips)"><rect class="shine" x="0" y="0" width="180" height="{H}" fill="url(#shine)"/></g>'
    css = ".shine{animation:sh 7s cubic-bezier(.5,0,.5,1) infinite}@keyframes sh{from{transform:translateX(-220px) skewX(-20deg)}55%,to{transform:translateX(900px) skewX(-20deg)}}"
    write("stack.svg", svg_doc(W, H, body, css, "Tech stack"))


# ---------------------------------------------------------------- timeline

def timeline():
    W, H = 840, 262
    y0, y1 = 2019.0, 2027.0
    left, right = 36, W - 36

    def X(year):
        return left + (year - y0) / (y1 - y0) * (right - left)

    now = 2026.79
    lanes = [
        ("NSUT", "B.Tech, Electronics & Communication", [(2019.58, 2023.5)], ("#3f3f46", "#52525b")),
        ("Startups & freelance", "Flutter → full stack → tech lead", [(2021.17, 2023.6)], (PURPLE, VIOLET)),
        ("Samsung R&D", "intern → SWE → Senior SWE", [(2022.33, 2022.58), (2023.6, 2026.37)], (BLUE, SKY)),
        ("Curvet", "Co-Founder & CTO", [(2026.37, now)], (PINK, PURPLE)),
    ]
    body = f"<defs>{grad('lane3', [(0, PINK), (1, PURPLE)])}</defs>{card_bg(W, H, 20)}"
    for yr in range(2019, 2028):
        x = X(yr)
        body += f'<path d="M{x:.1f} 26V{H - 44}" stroke="{BORDER}" stroke-opacity=".55" stroke-dasharray="2 5"/>'
        body += t(x, H - 22, str(yr), 11, fill=FAINT, wght=500, anchor="middle")
    xn = X(now)
    body += f'<path d="M{xn:.1f} 26V{H - 44}" stroke="{VIOLET}" stroke-opacity=".5" stroke-dasharray="3 3"/>'
    body += t(xn, 18, "now", 11, fill=VIOLET, wght=600, anchor="middle")
    for i, (name, role, spans, (c0, c1)) in enumerate(lanes):
        ly = 54 + i * 46
        gid = f"g{i}"
        body += grad(gid, [(0, c0), (1, c1)])
        last = i == len(lanes) - 1
        start, end = spans[-1]
        if last:
            label_w = tw(name, 13, wght=600) + tw("  " + role, 13)
            lx, anchor = X(end), "end"
        else:
            lx, anchor = X(spans[0][0]), "start"
        body += (
            f'<text x="{lx:.1f}" y="{ly}" class="i" font-size="13" text-anchor="{anchor}">'
            f'<tspan fill="{TEXT}" font-weight="600">{escape(name)}</tspan><tspan fill="{MUTED}">  {escape(role)}</tspan></text>'
        )
        for j, (a, b) in enumerate(spans):
            body += (
                f'<rect class="bar" style="animation-delay:{.15 + i * .18 + j * .08:.2f}s" x="{X(a):.1f}" y="{ly + 10}" '
                f'width="{X(b) - X(a):.1f}" height="8" rx="4" fill="url(#{gid})"/>'
            )
        if name == "Samsung R&D":
            px = X(2025.17)
            body += f'<circle cx="{px:.1f}" cy="{ly + 14}" r="5" fill="{BG}" stroke="#fff" stroke-width="1.5"/>'
        if last:
            body += (
                f'<circle cx="{xn:.1f}" cy="{ly + 14}" r="5" fill="#fff"/>'
                f'<circle cx="{xn:.1f}" cy="{ly + 14}" r="5" stroke="#fff" fill="none">'
                '<animate attributeName="r" values="5;14" dur="2s" repeatCount="indefinite"/>'
                '<animate attributeName="stroke-opacity" values=".7;0" dur="2s" repeatCount="indefinite"/></circle>'
            )
    css = (
        ".bar{transform-box:fill-box;transform-origin:left;"
        "animation:grow 1s cubic-bezier(.2,.7,.2,1) backwards}@keyframes grow{from{transform:scaleX(0)}}"
    )
    write("timeline.svg", svg_doc(W, H, body, css, "Career timeline, 2019 to now"))


# ---------------------------------------------------------------- link pills

PILLS = [
    ("pill-curvet.svg", "curvet.ai", True),
    ("pill-site.svg", "utkarshgupta.dev", False),
    ("pill-linkedin.svg", "LinkedIn", False),
    ("pill-x.svg", "X / Twitter", False),
    ("pill-npm.svg", "npm", False),
    ("pill-email.svg", "Email", False),
]


def pill(file, label, primary):
    h, size = 38, 13.5
    lw = tw(label, size, wght=500)
    icon = 22 if primary else 0
    w = 18 + icon + lw + 8 + tw("↗", size) + 16
    body = f"<defs>{grad('brand', [(0, PINK), (.4, PURPLE), (1, SKY)], 1, 1)}</defs>"
    body += f'<rect x=".75" y=".75" width="{w - 1.5:.1f}" height="{h - 1.5}" rx="{h / 2 - .75}" fill="{CARD}" stroke="{"url(#brand)" if primary else BORDER}" stroke-width="{1.5 if primary else 1}"/>'
    if primary:
        body += f'<g transform="translate(15 9.5) scale(.152)"><path d="{MARK}" fill="#fff"/></g>'
    body += t(18 + icon, 24, label, size, fill=TEXT if primary else SOFT, wght=500)
    body += t(18 + icon + lw + 7, 24, "↗", size, fill=VIOLET if primary else DIM)
    write(file, svg_doc(round(w), h, body, "", label))


# ---------------------------------------------------------------- footer

def footer():
    W, H = 840, 150
    s = 0.95
    lw, lh = 169 * s, 47 * s
    logo = "".join(f'<path d="{d}" fill="#fff"/>' for d in LOGO_PATHS)
    body = f"""
<defs>{blur_filter("soft", 50)}{GRAIN}<clipPath id="clip"><rect width="{W}" height="{H}" rx="22"/></clipPath></defs>
<g clip-path="url(#clip)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <g filter="url(#soft)" opacity=".5">
    <circle class="b1" cx="230" cy="190" r="110" fill="{PINK}"/>
    <circle class="b2" cx="420" cy="200" r="120" fill="{PURPLE}"/>
    <circle class="b1" cx="610" cy="190" r="110" fill="{SKY}"/>
  </g>
  <rect width="{W}" height="{H}" filter="url(#grain)" opacity=".06"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="21.5" stroke="#ffffff" stroke-opacity=".08"/>
<g transform="translate({(W - lw) / 2:.1f} 36) scale({s})">{logo}</g>
{t(W / 2, 36 + lh + 30, "Every model. One workspace.", 14, fill=MUTED, anchor="middle")}
"""
    css = (
        ".b1{animation:d1 12s ease-in-out infinite alternate}.b2{animation:d2 15s ease-in-out infinite alternate}"
        "@keyframes d1{to{transform:translate(80px,-20px)}}@keyframes d2{to{transform:translate(-90px,-10px)}}"
    )
    write("footer.svg", svg_doc(W, H, body, css, "Curvet: every model, one workspace"))


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    print("building assets/")
    hero()
    stats()
    router()
    terminal()
    for p in PROJECTS:
        project_card(p)
    stack()
    timeline()
    for args in PILLS:
        pill(*args)
    footer()

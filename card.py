"""Render card.svg: a retro player-select screen. Life is the game.

Stdlib only. Inputs: portrait.txt + portrait.shade (from portrait.py) and
ps2p.ttf (Press Start 2P, SIL OFL 1.1, subset to A-Z 0-9 and punctuation).
  python3 card.py
"""
import base64
import html

# ---- content: every line is from my life timeline / CV, nothing invented ----
QUEST = [
    "Go deep: one hard problem, real-world tech,",
    "and very smart people to build it with.",
    "Robots, in Munich. TUM.ai E-Lab, batch 6.",
]
SIDE_QUESTS = [  # 2026 only
    "Motorbiked solo over the Himalayas at 4,000 m",
    "Rebuilt a house in the redwoods after a wildfire",
    "Farmed + cooked for 10+ in the California hills",
    "Hunted alligators in Louisiana. Caught: 0",
    "Taught my 70-year-old godmother ChatGPT",
    "Built a 10-inch FPV drone from scratch. It flew",
    "Painted on a canvas headed for an SF gallery",
    "Got a few words in with Macron at VivaTech",
    "Y Combinator workshop + Claude Builders Cohort",
]
TROPHIES = [
    ("1ST", "Hermes Agent Hackathon, Paris"),
    ("WIN", "AI Paris Hack, $10K"),
    ("2ND", "ETHGlobal Lisbon + Lovable 42"),
    ("3RD", "Euro Hackathon League (BMW) + Dogathon SF"),
    ("TOP5", "SF robotics hack, first time touching hardware"),
]
LORE = [
    ("19", "founded Follege: 10K+ students, then COVID"),
    ("BKK", "product lead, Ampverse: 80K+ signups"),
    ("PAR", "Ledger: shipped 6+ blockchain integrations"),
    ("MUC", "TUM x HEC Paris double degree"),
]
STATS = [  # name, 0-10, label
    ("CURIOSITY", 10, "MAX"),
    ("GRIT", 9, ""),
    ("HACKATHONS", 9, "1+/WK"),
    ("COOKING", 7, ""),
    ("MUAY THAI", 6, ""),
    ("SLEEP", 2, "LOW"),
]
MAP = "Lived: India, Thailand, France, UK, Germany. 30+ countries visited"

# ---- palette: synthwave arcade ----
BG, PANEL, LINE = "#140c26", "#1d1236", "#3a2763"
PINK, CYAN, YELLOW, TEXT, DIM, GREEN = "#ff4fa3", "#3ee6ff", "#ffd23f", "#f3ecff", "#9a8cc4", "#7dff9a"
# portrait shade 0..15 runs through this gradient (dark violet -> pink -> gold -> cream)
STOPS = [(0, (96, 46, 150)), (3, (214, 70, 160)), (7, (255, 128, 128)), (11, (255, 212, 120)), (15, (255, 248, 228))]

W, H = 980, 920
PX = "font-family:PS2P,monospace"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
P_FS, P_LH = 7.6, 8.8                  # portrait glyph size / line height
LX, RX = 34, 450                       # left / right column x


def esc(s):
    return html.escape(s, quote=False)


def shade_rgb(v):
    for (a, ca), (b, cb) in zip(STOPS, STOPS[1:]):
        if a <= v <= b:
            t = (v - a) / (b - a)
            return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(ca, cb))


def portrait(x0, y0):
    chars = open("portrait.txt").read().rstrip("\n").split("\n")
    shades = open("portrait.shade").read().rstrip("\n").split("\n")
    out = []
    for i, (line, sh) in enumerate(zip(chars, shades)):
        spans, run, cur = [], "", None
        for ch, s in zip(line, sh):
            if ch == " " and cur is not None:
                s = cur
            if s != cur and run:
                spans.append(f'<tspan class="s{cur}">{esc(run)}</tspan>')
                run = ""
            cur, run = s, run + ch
        if run.strip():
            spans.append(f'<tspan class="s{cur}">{esc(run)}</tspan>')
        if spans:
            out.append(f'<text x="{x0}" y="{y0 + i * P_LH:.1f}" class="p r" '
                       f'style="animation-delay:{0.2 + i * 0.025:.2f}s">{"".join(spans)}</text>')
    return "\n".join(out), len(chars) * P_LH, max(map(len, chars))


def heading(x, y, text, color, delay):
    return (f'<text x="{x}" y="{y}" class="px r" fill="{color}" style="animation-delay:{delay:.2f}s">'
            f'{esc(text)}</text>')


def render():
    font = base64.b64encode(open("ps2p.ttf", "rb").read()).decode()
    shade_css = "".join(f".s{v:x}{{fill:{shade_rgb(v)}}}" for v in range(16))
    parts = []

    # top bar
    parts.append(f'<text x="{LX}" y="52" class="px" font-size="15" fill="{YELLOW}">PLAYER 1</text>')
    parts.append(f'<text x="{W / 2}" y="52" class="px" font-size="15" fill="{TEXT}" text-anchor="middle">'
                 f'LIFE: THE GAME</text>')
    parts.append(f'<text x="{W - LX}" y="52" class="px" font-size="15" fill="{CYAN}" text-anchor="end">'
                 f'SAVE 2026</text>')
    parts.append(f'<line x1="{LX}" x2="{W - LX}" y1="70" y2="70" stroke="{LINE}" stroke-width="2" stroke-dasharray="6 6"/>')

    # left: portrait in a frame, nameplate, stat bars
    rows, p_h, p_w = portrait(LX + 14, 112)
    pw = p_w * P_FS * 0.6 + 28
    parts.append(f'<rect x="{LX}" y="90" width="{pw:.0f}" height="{p_h + 34:.0f}" fill="{PANEL}" stroke="{PINK}" stroke-width="3"/>')
    parts.append(rows)
    y = 90 + p_h + 34 + 40
    parts.append(f'<text x="{LX}" y="{y}" class="px" font-size="22" fill="{TEXT}">ABHI</text>')
    parts.append(f'<text x="{LX + 104}" y="{y}" class="px" font-size="10" fill="{DIM}">ABHINAV SINGH</text>')
    y += 26
    parts.append(f'<text x="{LX}" y="{y}" class="px" font-size="10" fill="{PINK}">CLASS: LIFEMAXXER</text>')
    y += 34
    bar_x, seg = LX + 132, 21
    for i, (name, val, label) in enumerate(STATS):
        d = 1.0 + i * 0.12
        parts.append(f'<text x="{LX}" y="{y + 11}" class="px" font-size="9" fill="{TEXT}">{name}</text>')
        for j in range(10):
            fill = (PINK if val >= 9 else CYAN if val >= 5 else YELLOW) if j < val else LINE
            cls = ' class="seg"' if j < val else ""
            parts.append(f'<rect x="{bar_x + j * seg}" y="{y}" width="{seg - 4}" height="13" fill="{fill}"{cls} '
                         f'style="animation-delay:{d + j * 0.05:.2f}s"/>')
        if label:
            parts.append(f'<text x="{bar_x + 10 * seg + 6}" y="{y + 11}" class="px" font-size="8" fill="{DIM}">{label}</text>')
        y += 25

    # right: quest log
    y = 108
    t = 0.6
    parts.append(heading(RX, y, "> CURRENT QUEST", YELLOW, t))
    for line in QUEST:
        y += 22
        t += 0.08
        parts.append(f'<text x="{RX}" y="{y}" class="m r" fill="{TEXT}" style="animation-delay:{t:.2f}s">{esc(line)}</text>')

    y += 42
    t += 0.15
    parts.append(heading(RX, y, f"> SIDE QUESTS CLEARED  {len(SIDE_QUESTS)}/{len(SIDE_QUESTS)}", PINK, t))
    for q in SIDE_QUESTS:
        y += 22
        t += 0.12
        parts.append(f'<text x="{RX}" y="{y}" class="m r" style="animation-delay:{t:.2f}s">'
                     f'<tspan fill="{GREEN}">[x]</tspan><tspan fill="{TEXT}"> {esc(q)}</tspan></text>')

    y += 42
    t += 0.15
    parts.append(heading(RX, y, "> TROPHIES", CYAN, t))
    for rank, what in TROPHIES:
        y += 22
        t += 0.1
        parts.append(f'<text x="{RX}" y="{y}" class="m r" style="animation-delay:{t:.2f}s">'
                     f'<tspan fill="{YELLOW}" font-weight="700">{rank:<5}</tspan><tspan fill="{TEXT}">{esc(what)}</tspan></text>')

    y += 42
    t += 0.15
    parts.append(heading(RX, y, "> PREVIOUS SAVES", DIM, t))
    for tag, what in LORE:
        y += 22
        t += 0.08
        parts.append(f'<text x="{RX}" y="{y}" class="m r" style="animation-delay:{t:.2f}s">'
                     f'<tspan fill="{CYAN}">{tag:<5}</tspan><tspan fill="{DIM}">{esc(what)}</tspan></text>')

    # footer
    fy = H - 66
    parts.append(f'<line x1="{LX}" x2="{W - LX}" y1="{fy - 30}" y2="{fy - 30}" stroke="{LINE}" stroke-width="2" stroke-dasharray="6 6"/>')
    parts.append(f'<text x="{LX}" y="{fy}" class="m" fill="{DIM}">{esc(MAP)}</text>')
    parts.append(f'<text x="{LX}" y="{fy + 30}" class="px blink" font-size="13" fill="{YELLOW}">PRESS START: PMABHI.COM</text>')
    parts.append(f'<text x="{W - LX}" y="{fy + 30}" class="px" font-size="10" fill="{PINK}" text-anchor="end">'
                 f'INSERT COIN: CAL.COM/PMABHI/30MIN</text>')

    body = "\n".join(parts)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<title>ABHI, player 1. Class: lifemaxxer.</title>
<desc>Abhi (Abhinav Singh), Munich. Life is a game. 2026: motorbiked solo over the Himalayas, rebuilt a house after a wildfire in the redwoods, built an FPV drone, won the Hermes Agent Hackathon Paris, 2nd at ETHGlobal Lisbon. Now going deep on robotics at TUM. pmabhi.com</desc>
<defs>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity=".22"/></pattern>
<radialGradient id="glow" cx="50%" cy="40%" r="75%"><stop offset="0" stop-color="#2a1550"/><stop offset="1" stop-color="{BG}"/></radialGradient>
</defs>
<style>
@font-face{{font-family:PS2P;src:url(data:font/ttf;base64,{font}) format("truetype")}}
.px{{{PX};font-size:12px}}
.m{{font-family:{MONO};font-size:14px;white-space:pre}}
.p{{font-family:{MONO};font-size:{P_FS}px;white-space:pre}}
{shade_css}
.r{{opacity:0;animation:on .3s ease-out forwards}}
@keyframes on{{from{{opacity:0;transform:translateY(4px)}}to{{opacity:1;transform:none}}}}
.seg{{opacity:0;animation:on .12s steps(1) forwards}}
.blink{{animation:blink 1.1s steps(1) infinite}}
@keyframes blink{{60%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.r,.seg{{opacity:1;animation:none}}.blink{{animation:none}}}}
</style>
<rect width="{W}" height="{H}" rx="16" fill="url(#glow)"/>
<rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="10" fill="none" stroke="{CYAN}" stroke-width="2" opacity=".55"/>
<rect x="14" y="14" width="{W - 28}" height="{H - 28}" rx="6" fill="none" stroke="{PINK}" stroke-width="2" opacity=".55"/>
{body}
<rect width="{W}" height="{H}" rx="16" fill="url(#scan)" pointer-events="none"/>
</svg>
'''


if __name__ == "__main__":
    svg = render()
    open("card.svg", "w").write(svg)
    print(f"card.svg {len(svg):,} bytes")

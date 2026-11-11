"""Render card.svg: a terminal window running neofetch on me.

Stdlib only, so the daily GitHub Action needs no installs.
  GITHUB_TOKEN=... python3 build.py      live GitHub stats
  python3 build.py --offline             placeholder stats (layout work)
"""
import datetime as dt
import html
import json
import os
import sys
import urllib.request

LOGIN = "abhinxx"
SINCE = dt.date(2019, 6, 10)  # first day on GitHub, drives "Uptime"

# ---- the case for me. Every line is sourced from my CV / profile notes. ----
INFO = [
    ("OS", "Product brain, engineer hands"),
    ("Uptime", "{uptime}"),
    ("Host", "TUM x HEC Paris, MSc Mgmt & Tech double degree"),
    ("Kernel", "B.Tech Software Engineering, DTU"),
    ("Shell", "Claude Code, Codex, Hermes Agent"),
    ("Now", "Entrepreneur in Residence, TUM.ai E-Lab"),
    ("Also", "Founder Scout, Pioneers VC"),
    None,
    ("Shipped.Ledger", "6+ concurrent integrations, 20+ people led"),
    ("Shipped.Canton", "mainnet MVP in under a month, $2M+ reward"),
    ("Shipped.Ampverse", "80K+ registrations, 100M+ content views"),
    ("Chains", "Canton, Aleo, Concordium, Circle Arc, Zcash"),
    ("Code", "Python, TypeScript, Swift, Rust, Solidity"),
    ("Speaks", "English, Hindi, French, Japanese"),
    ("Top.Langs", "{langs}"),
    ("- Wins", None),
    ("1st", "Global Hermes AI Hackathon, AI Paris Hack ($10K)"),
    ("2nd", "ETHGlobal Lisbon, Lovable 42"),
    ("3rd", "European Hackathon League finals (BMW), Dogathon SF"),
    ("Cadence", "a hackathon most weeks"),
    ("- Contact", None),
    ("Web", "pmabhi.com"),
    ("LinkedIn", "in/abhixx"),
    ("Call", "cal.com/pmabhi/30min"),
    ("Base", "Munich, DE"),
    ("- GitHub", None),
    ("STATS", None),
]
WIDTH_CH = 64  # info column width in characters

# ---- layout (px) ----
W = 1080
BAR = 34                       # window title bar
PAD = 22
P_FS, P_LH, P_CW = 10.6, 12.2, 6.36     # portrait font size / line height / char width
I_FS, I_LH = 13.5, 19.2                 # info font size / line height
INFO_X = 512
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"


def gql(query, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": LOGIN},
    )
    out = json.load(urllib.request.urlopen(req, timeout=30))
    if "errors" in out:
        raise SystemExit(out["errors"])
    return out["data"]


def stats(token):
    u = gql(f"""query{{user(login:"{LOGIN}"){{
      createdAt followers{{totalCount}}
      repositories(ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC,first:100){{
        totalCount nodes{{stargazerCount
          languages(first:8,orderBy:{{field:SIZE,direction:DESC}}){{edges{{size node{{name}}}}}}}}}}
      repositoriesContributedTo(contributionTypes:[COMMIT,PULL_REQUEST],includeUserRepositories:false){{totalCount}}
    }}}}""", token)["user"]
    # all-time contributions = what the profile graph shows, summed per year
    start = int(u["createdAt"][:4])
    years = range(start, dt.date.today().year + 1)
    q = " ".join(
        f'y{y}:contributionsCollection(from:"{y}-01-01T00:00:00Z",to:"{y}-12-31T23:59:59Z")'
        "{contributionCalendar{totalContributions} totalCommitContributions restrictedContributionsCount}"
        for y in years)
    c = gql(f'query{{user(login:"{LOGIN}"){{{q}}}}}', token)["user"]
    langs = {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:3]
    this_year = c[f"y{dt.date.today().year}"]["contributionCalendar"]["totalContributions"]
    return {
        "repos": u["repositories"]["totalCount"],
        "contributed": u["repositoriesContributedTo"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "followers": u["followers"]["totalCount"],
        "contrib": sum(v["contributionCalendar"]["totalContributions"] for v in c.values()),
        "year": this_year,
        "langs": " . ".join(f"{n} {round(s * 100 / total)}%" for n, s in top),
    }


def uptime(today):
    y, m, d = today.year - SINCE.year, today.month - SINCE.month, today.day - SINCE.day
    if d < 0:
        m -= 1
        d += (today.replace(day=1) - dt.timedelta(days=1)).day
    if m < 0:
        y, m = y - 1, m + 12
    s = lambda n, w: f"{n} {w}{'' if n == 1 else 's'}"
    return f"{s(y, 'year')}, {s(m, 'month')}, {s(d, 'day')}"


def esc(s):
    return html.escape(s, quote=False)


def kv_line(key, val):
    """key ........ value, as tspans so key/dots/value get their own colour."""
    dots = WIDTH_CH - len(key) - len(val) - 4
    return (f'<tspan class="k">{esc(key)}</tspan><tspan class="d">: {"." * max(2, dots)} </tspan>'
            f'<tspan class="v">{esc(val)}</tspan>')


def rule_line(title):
    return f'<tspan class="h">{esc(title)} </tspan><tspan class="d">{"-" * (WIDTH_CH - len(title) - 1)}</tspan>'


def stats_lines(st):
    a = f"{st['repos']} {{Contributed: {st['contributed']}}}"
    b = str(st["stars"])
    c = f"{st['contrib']:,}"
    d = f"{st['year']:,}"  # this year alone: the curve is going up
    half = WIDTH_CH // 2 + 4

    def pair(k1, v1, k2, v2):
        left = f'<tspan class="k">{k1}</tspan><tspan class="d">: {"." * (half - len(k1) - len(v1) - 4)} </tspan><tspan class="v">{esc(v1)}</tspan>'
        n = WIDTH_CH - half - len(k2) - len(v2) - 6
        return left + f'<tspan class="d"> | </tspan><tspan class="k">{k2}</tspan><tspan class="d">: {"." * n} </tspan><tspan class="v">{esc(v2)}</tspan>'

    return [
        pair("Repos", a, "Stars", b),
        pair("Contributions", c, str(dt.date.today().year), d),
    ]


def portrait():
    chars = open("portrait.txt").read().rstrip("\n").split("\n")
    shades = open("portrait.shade").read().rstrip("\n").split("\n")
    rows = []
    for line, sh in zip(chars, shades):
        spans, run, cur = [], "", None
        for ch, s in zip(line, sh):
            if ch == " ":
                s = cur if cur is not None else s     # spaces join any run
            if s != cur and run:
                spans.append(f'<tspan class="s{cur}">{esc(run)}</tspan>')
                run = ""
            cur = s
            run += ch
        if run.strip():
            spans.append(f'<tspan class="s{cur}">{esc(run)}</tspan>')
        rows.append("".join(spans))
    return rows


def render(st):
    today = dt.date.today()
    fill = {"uptime": uptime(today), "langs": st["langs"]}
    lines = [f'<tspan class="u">abhi</tspan><tspan class="d">@</tspan><tspan class="u">munich</tspan> '
             f'<tspan class="d">{"-" * (WIDTH_CH - 12)}</tspan>']
    for item in INFO:
        if item is None:
            lines.append("")
        elif item[0] == "STATS":
            lines += stats_lines(st)
        elif item[1] is None:
            lines += ["", rule_line(item[0])]
        else:
            lines.append(kv_line(item[0], item[1].format(**fill)))

    prow = portrait()
    top = BAR + PAD + 26                     # below the typed prompt
    p_h = len(prow) * P_LH
    i_h = len(lines) * I_LH
    body = max(p_h, i_h)
    H = int(top + body + 50)
    p_y = top + (body - p_h) / 2 + P_FS
    i_y = top + (body - i_h) / 2 + I_FS

    shade_css = "".join(
        f".s{v:x}{{fill:rgb({g},{g},{int(g * 1.04) if g < 245 else 255})}}"
        for v in range(16) for g in [int(70 + 185 * (v / 15) ** 0.9)])
    # stagger: portrait scans in top to bottom, info streams line by line
    p_rows = "\n".join(
        f'<text x="{PAD + 6}" y="{p_y + i * P_LH:.1f}" class="p r" style="animation-delay:{0.9 + i * 0.03:.2f}s">{r}</text>'
        for i, r in enumerate(prow) if r)
    i_rows = "\n".join(
        f'<text x="{INFO_X}" y="{i_y + i * I_LH:.1f}" class="i r" style="animation-delay:{1.1 + i * 0.07:.2f}s">{l}</text>'
        for i, l in enumerate(lines) if l)
    end = 1.1 + len(lines) * 0.07 + 0.2
    cmd = "neofetch --make-the-case"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">
<title>abhi@munich: neofetch</title>
<desc>Abhi (Abhinav Singh). Product brain, engineer hands. TUM x HEC Paris. Ex-Ledger, shipped 6+ chain integrations. Hackathon winner. pmabhi.com</desc>
<style>
.p{{font-size:{P_FS}px;white-space:pre}}
.i{{font-size:{I_FS}px;white-space:pre}}
.k{{fill:#ffa657}} .v{{fill:#a5d6ff}} .d{{fill:#5a6370}} .h{{fill:#e6edf3;font-weight:700}} .u{{fill:#7ee787;font-weight:700}}
{shade_css}
.r{{opacity:0;animation:on .25s ease-out forwards}}
@keyframes on{{from{{opacity:0;transform:translateX(-6px)}}to{{opacity:1;transform:none}}}}
.cmd{{clip-path:inset(0 100% 0 0);animation:type .8s steps({len(cmd)}) .25s forwards}}
@keyframes type{{to{{clip-path:inset(0 0 0 0)}}}}
.cur{{animation:blink 1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.late{{opacity:0;animation:on .2s {end:.2f}s forwards}}
@media (prefers-reduced-motion:reduce){{.r,.late{{opacity:1;animation:none}}.cmd{{clip-path:none;animation:none}}}}
</style>
<rect width="{W}" height="{H}" rx="12" fill="#0d1117"/>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="#30363d"/>
<path d="M12 .5h{W - 24}a11.5 11.5 0 0 1 11.5 11.5v{BAR - 12}h-{W - 1}v-{BAR - 12}A11.5 11.5 0 0 1 12 .5z" fill="#161b22"/>
<circle cx="20" cy="{BAR / 2}" r="6" fill="#ff5f57"/><circle cx="40" cy="{BAR / 2}" r="6" fill="#febc2e"/><circle cx="60" cy="{BAR / 2}" r="6" fill="#28c840"/>
<text x="{W / 2}" y="{BAR / 2 + 4.5}" text-anchor="middle" font-size="12.5" fill="#8b949e">abhi@munich: ~</text>
<text x="{PAD + 6}" y="{BAR + PAD + 4}" class="i"><tspan class="u">abhi@munich</tspan><tspan class="d"> ~ % </tspan></text>
<text x="{PAD + 6 + 16 * I_FS * 0.6:.1f}" y="{BAR + PAD + 4}" class="i cmd" fill="#e6edf3">{cmd}</text>
{p_rows}
{i_rows}
<g class="late"><text x="{PAD + 6}" y="{H - 22}" class="i"><tspan class="u">abhi@munich</tspan><tspan class="d"> ~ % </tspan></text>
<rect class="cur" x="{PAD + 6 + 16 * I_FS * 0.6:.1f}" y="{H - 22 - I_FS + 2}" width="8" height="{I_FS + 2}" fill="#e6edf3"/>
<text x="{W - PAD}" y="{H - 22}" text-anchor="end" font-size="11" fill="#5a6370">refreshed {today.isoformat()} by a GitHub Action</text></g>
</svg>
'''


def main():
    if "--offline" in sys.argv:
        st = {"repos": 0, "contributed": 0, "stars": 0, "followers": 0, "contrib": 0,
              "year": 0, "langs": "offline"}
    else:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if not token:
            raise SystemExit("set GITHUB_TOKEN (or pass --offline)")
        st = stats(token)
    svg = render(st)
    open("card.svg", "w").write(svg)
    print(f"card.svg {len(svg):,} bytes", json.dumps(st))


if __name__ == "__main__":
    main()

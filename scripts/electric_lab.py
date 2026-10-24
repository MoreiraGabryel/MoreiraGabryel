"""Build the Electric Lab artwork using only Python's standard library."""

import argparse
from datetime import date, datetime, timedelta, timezone
from html import escape
import json
import math
import os
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET


QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositories(first: 30, privacy: PUBLIC, ownerAffiliations: OWNER,
                 isFork: false, orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes { name url pushedAt isArchived }
    }
  }
}
"""

THEMES = {
    "dark": {
        "bg": "#0B1018", "panel": "#101B2A", "ink": "#F0F5FC",
        "muted": "#A3B4CB", "line": "#23374E", "blue": "#53C7FF",
        "yellow": "#F4D35E", "dim": "#203C55", "grid": "#142233",
    },
    "light": {
        "bg": "#F3F7FC", "panel": "#E6EFF9", "ink": "#12243B",
        "muted": "#4B617B", "line": "#BDCEE1", "blue": "#0969B5",
        "yellow": "#8C6200", "dim": "#B4CEE6", "grid": "#E1EAF4",
    },
}


def fetch_activity(login, now):
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("Set GH_TOKEN or GITHUB_TOKEN, or use --snapshot.")
    start = now.date() - timedelta(days=29)
    variables = {
        "login": login,
        "from": f"{start.isoformat()}T00:00:00Z",
        "to": now.isoformat().replace("+00:00", "Z"),
    }
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json", "User-Agent": "electric-lab"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        payload = json.load(response)
    if payload.get("errors") or not payload.get("data", {}).get("user"):
        raise RuntimeError("GitHub did not return complete activity data.")
    return normalize(payload["data"]["user"], login, now)


def normalize(user, login, now):
    """Keep exactly 30 UTC calendar days, including today; reject partial data."""
    end = now.date()
    start = end - timedelta(days=29)
    calendar = user["contributionsCollection"]["contributionCalendar"]
    counts = {
        day["date"]: day["contributionCount"]
        for week in calendar["weeks"] for day in week["contributionDays"]
        if start.isoformat() <= day["date"] <= end.isoformat()
    }
    days = []
    for index in range(30):
        day = (start + timedelta(days=index)).isoformat()
        count = counts.get(day)
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ValueError(f"Missing or invalid contribution count: {day}")
        days.append({"date": day, "count": count})
    repositories = [
        repo for repo in user["repositories"]["nodes"]
        if repo["name"].lower() != login.lower()
        and not repo["isArchived"] and repo["pushedAt"]
    ]
    latest = max(repositories, key=lambda repo: repo["pushedAt"], default=None)
    return {
        "username": login,
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "days": days,
        "total": sum(day["count"] for day in days),
        "active_days": sum(day["count"] > 0 for day in days),
        "latest_repository": (
            {key: latest[key] for key in ("name", "url", "pushedAt")}
            if latest else None
        ),
    }


def text(x, y, value, size=16, fill="ink", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" '
            f'class="{fill}" {extra}>{escape(str(value))}</text>')


def monogram(x, y, scale=1):
    # Custom MG circuit: static geometry stays visible when animation is disabled.
    return f'''<g transform="translate({x} {y}) scale({scale})" aria-hidden="true">
      <circle r="137" fill="url(#aura)"/>
      <circle r="122" class="wire" stroke-dasharray="2 12"/>
      <circle r="103" class="wire"/>
      <g class="orbit"><path d="M0 -122 A122 122 0 0 1 122 0" class="accent-wire"/>
        <circle cx="122" r="4" class="spark"/></g>
      <path d="M-150 -60 H-116 L-88 -32 M150 60 H116 L88 32
               M-65 -150 V-120 L-44 -99 M65 150 V120 L44 99" class="wire"/>
      <path d="M-72 43 V-42 L-39 -8 L-6 -42 V43
               M73 -42 H37 L15 -20 V22 L37 43 H77 V4 H48"
            class="monogram"/>
      <path d="M-72 43 V-42 L-39 -8 L-6 -42 V43
               M73 -42 H37 L15 -20 V22 L37 43 H77 V4 H48"
            class="current"/>
      <circle cx="-72" cy="43" r="4" class="spark"/>
      <circle cx="48" cy="4" r="4" class="spark"/>
      <path d="M-12 67 H16 L5 83 H25 L-7 111 L0 91 H-17 Z" class="spark"/>
    </g>'''


def render_hero(activity, theme="dark", mobile=False, static=False):
    colors = THEMES[theme]
    width, height = (600, 800) if mobile else (1200, 584)
    margin = 36 if mobile else 52
    total, active = activity["total"], activity["active_days"]
    days = activity["days"]
    first, last = date.fromisoformat(days[0]["date"]), date.fromisoformat(days[-1]["date"])
    generated = datetime.fromisoformat(activity["generated_at"].replace("Z", "+00:00"))
    repo = activity["latest_repository"]
    latest_name = repo["name"] if repo else "Sem projeto público recente"
    limit = 32 if mobile else 48
    if len(latest_name) > limit:
        latest_name = latest_name[:limit - 1] + "…"
    styles = "\n".join(f".{key} {{ fill: {value}; }}" for key, value in colors.items())
    motion = "" if static else '''
      .orbit { animation: orbit 24s linear infinite; }
      .current { animation: flow 7s linear infinite; }
      .signal { animation: flow 12s linear infinite; }
      @keyframes orbit { to { transform: rotate(360deg); } }
      @keyframes flow { to { stroke-dashoffset: -500; } }
      @media (prefers-reduced-motion: reduce) {
        .orbit, .current, .signal { animation: none; }
      }
    '''
    svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
      viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
      <title id="title">Marcos Gabryel — Electric Lab</title>
      <desc id="desc">Desenvolvimento Full Stack, automação e agentes de IA.
      {total} contribuições em {active} dias ativos entre {first} e {last}.
      Cada ponto da malha representa um dia; altura e intensidade indicam contribuições.
      Gerado em {escape(activity['generated_at'])}. Último projeto público: {escape(repo['name'] if repo else 'nenhum')}.</desc>
      <defs>
        <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
          <circle cx="1" cy="1" r="1" fill="{colors['line']}" opacity=".5"/>
        </pattern>
        <radialGradient id="aura">
          <stop stop-color="{colors['blue']}" stop-opacity=".12"/>
          <stop offset="1" stop-color="{colors['blue']}" stop-opacity="0"/>
        </radialGradient>
        <linearGradient id="edge"><stop stop-color="{colors['blue']}"/>
          <stop offset=".7" stop-color="{colors['blue']}" stop-opacity=".15"/>
          <stop offset="1" stop-color="{colors['yellow']}"/></linearGradient>
      </defs>
      <style>
        text {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; }}
        .mono {{ font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', monospace; }}
        {styles}
        .wire {{ fill: none; stroke: {colors['line']}; stroke-width: 1.5; }}
        .accent-wire {{ fill: none; stroke: {colors['blue']}; stroke-width: 2; }}
        .spark {{ fill: {colors['yellow']}; }}
        .monogram {{ fill: none; stroke: {colors['blue']}; stroke-width: 5; stroke-linejoin: bevel; }}
        .current {{ fill: none; stroke: {colors['yellow']}; stroke-width: 5;
          stroke-dasharray: 24 476; stroke-linecap: round; }}
        .signal {{ fill: none; stroke: {colors['yellow']}; stroke-width: 2;
          stroke-dasharray: 18 482; }}
        {motion}
      </style>
      <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="24"
        fill="{colors['bg']}" stroke="{colors['line']}"/>
      <rect x="20" y="20" width="{width - 40}" height="{height - 40}" rx="16" fill="url(#grid)"/>
      <path d="M{margin} 1 H{width - margin}" stroke="url(#edge)" stroke-width="3"/>
    ''']
    svg.append(text(margin, 51, "MG / ELECTRIC LAB", 14, "blue", 'letter-spacing="3"'))
    if mobile:
        svg.extend([
            monogram(478, 186, .52),
            text(margin, 145, "Marcos", 64, extra='font-weight="750" letter-spacing="-3"'),
            text(margin, 212, "Gabryel.", 68, extra='font-weight="750" letter-spacing="-3"'),
            text(margin, 267, "FULL STACK DEVELOPER", 16, "blue", 'letter-spacing="2"'),
            text(margin, 305, "Código, automação", 25),
            text(margin, 339, "e ideias em movimento.", 25),
            text(margin, 380, "JAVA / SPRING / TYPESCRIPT / REACT", 13, "muted"),
            text(margin, 445, "30 DIAS EM CIRCUITO", 13, "blue", 'letter-spacing="2"'),
            text(margin, 490, str(total), 36, extra='font-weight="700"'),
            text(margin + 88, 488, "contribuições", 16, "muted"),
            text(365, 490, f"{active}/30", 27, extra='font-weight="700"'),
            text(451, 488, "dias ativos", 14, "muted"),
        ])
        graph_top, graph_bottom = 528, 619
        footer_y = 665
    else:
        svg.extend([
            text(width - margin, 51, "@MoreiraGabryel", 14, "muted", 'text-anchor="end"'),
            text(margin, 147, "Marcos Gabryel.", 76, extra='font-weight="750" letter-spacing="-4"'),
            text(margin + 2, 192, "FULL STACK DEVELOPER", 17, "blue", 'letter-spacing="3"'),
            text(margin, 248, "Código, automação e ideias em movimento.", 25),
            text(margin, 289, "JAVA / SPRING / TYPESCRIPT / REACT", 14, "muted", 'letter-spacing="1.5"'),
            monogram(978, 198),
            text(margin, 367, "30 DIAS EM CIRCUITO", 13, "blue", 'letter-spacing="2"'),
            text(width - margin, 367, f"{total} contribuições  /  {active} dias ativos", 16, "muted", 'text-anchor="end"'),
        ])
        graph_top, graph_bottom = 398, 475
        footer_y = 511
    svg.append(f'<path d="M{margin} {408 if mobile else 327} H{width - margin}" class="wire"/>')
    peak = max(1, max(day["count"] for day in days))
    points = []
    for i, day in enumerate(days):
        x = margin + i * (width - margin * 2) / 29
        # Square-root scaling keeps low activity visible alongside peak days.
        y = graph_bottom - math.sqrt(day["count"] / peak) * (graph_bottom - graph_top)
        points.append((round(x, 2), round(y, 2)))
    path = "M" + " L".join(f"{x} {y}" for x, y in points)
    svg.append(f'<path d="M{margin} {graph_bottom} H{width - margin}" class="wire" stroke-dasharray="3 6"/>')
    svg.append(f'<path d="{path}" class="accent-wire" opacity=".6"/>')
    svg.append(f'<path d="{path}" class="signal"/>')
    for day, (x, y) in zip(days, points):
        color = "blue" if day["count"] else "dim"
        radius = 3.5 if mobile else 4.5
        svg.append(f'<path d="M{x} {y} V{graph_bottom}" class="wire"/>')
        svg.append(f'<circle cx="{x}" cy="{y}" r="{radius}" class="{color}"><title>{day["date"]}: {day["count"]} contribuições</title></circle>')
    period = f"{first:%d.%m} — {last:%d.%m.%Y}"
    svg.append(text(margin, footer_y, period, 12, "muted"))
    svg.append(text(width - margin, footer_y, "1 PONTO = 1 DIA", 11, "muted", 'text-anchor="end" letter-spacing="1"'))
    if mobile:
        svg.append(text(margin, 710, "ÚLTIMO PUSH EM PROJETO PÚBLICO", 11, "blue", 'letter-spacing="1"'))
        svg.append(text(margin, 737, latest_name, 18))
        svg.append(text(margin, 772, f"SNAPSHOT / {generated:%d.%m.%Y %H:%M} UTC", 11, "muted"))
    else:
        svg.append(text(margin, 552, f"ÚLTIMO PUSH PÚBLICO / {latest_name}", 13, "muted"))
        svg.append(text(width - margin, 552, f"SNAPSHOT / {generated:%d.%m.%Y %H:%M} UTC", 11, "muted", 'text-anchor="end"'))
    svg.append("</svg>\n")
    result = "\n".join(svg)
    ET.fromstring(result)
    return result


def build(activity, output):
    output.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        for mobile in (False, True):
            suffix = "-mobile" if mobile else ""
            for static in (False, True):
                motion = "-static" if static else ""
                filename = f"hero-{theme}{suffix}{motion}.svg"
                (output / filename).write_text(
                    render_hero(activity, theme, mobile, static), encoding="utf-8"
                )
    (output / "activity.json").write_text(
        json.dumps(activity, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", default="MoreiraGabryel")
    parser.add_argument("--output", type=Path, default=Path("dist"))
    parser.add_argument("--snapshot", type=Path, help="Rebuild from a saved activity.json without network access")
    args = parser.parse_args()
    activity = (json.loads(args.snapshot.read_text(encoding="utf-8")) if args.snapshot
                else fetch_activity(args.username, datetime.now(timezone.utc).replace(microsecond=0)))
    build(activity, args.output)
    print(f"Electric Lab: {activity['total']} contributions, {activity['active_days']} active days; {args.output}")


if __name__ == "__main__":
    main()

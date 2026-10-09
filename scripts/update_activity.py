"""Render the profile's last 31 days of GitHub contributions without a third-party service."""
import json
import math
import subprocess
from datetime import date, timedelta
from pathlib import Path

query = 'query { user(login:"Sahad-09") { contributionsCollection { contributionCalendar { weeks { contributionDays { date contributionCount } } } } } }'
data = json.loads(subprocess.check_output(['gh', 'api', 'graphql', '-f', 'query=' + query]))
calendar = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
today = date.today()
start = today - timedelta(days=30)
days = [d for w in calendar for d in w['contributionDays'] if start <= date.fromisoformat(d['date']) <= today]
if len(days) != 31:
    raise ValueError('Expected a complete 31-day contribution calendar')
width, height = 1000, 310
left, right, top, bottom = 60, 970, 75, 248
peak = max(4, max(d['contributionCount'] for d in days))
step = max(1, math.ceil(peak / 4))
scale = step * 4
points = [(left + i * (right-left)/30, bottom - d['contributionCount']*(bottom-top)/scale) for i,d in enumerate(days)]
line = ' '.join(f'{x:.1f},{y:.1f}' for x,y in points)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
'<title id="title">Sahad’s GitHub Activity Graph</title>',
f'<desc id="desc">Daily contributions from {start.isoformat()} to {today.isoformat()}. {sum(d["contributionCount"] for d in days)} contributions in total.</desc>',
'<rect width="1000" height="310" rx="12" fill="#0b111b"/>',
'<g font-family="Arial, sans-serif" fill="#b6cbdd">',
'<text x="500" y="36" font-size="21" text-anchor="middle" fill="#dde8f0">Sahad’s GitHub Activity Graph</text>']
for i in range(5):
    n=i*step; y=bottom-n*(bottom-top)/scale
    svg += [f'<path d="M{left} {y:.1f}H{right}" stroke="#233345" stroke-width="1"/>',f'<text x="46" y="{y+4:.1f}" font-size="11" text-anchor="end">{n}</text>']
svg += [f'<polygon points="{left},{bottom} {line} {right},{bottom}" fill="#334d66" opacity="0.45"/>',f'<polyline points="{line}" fill="none" stroke="#88a9c3" stroke-width="2.5" stroke-linejoin="round"/>']
for i,((x,y),d) in enumerate(zip(points, days)):
    svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#e6edf3"><title>{d["date"]}: {d["contributionCount"]} contributions</title></circle>')
    if i%5 == 0:
        label=date.fromisoformat(d['date']).strftime('%d %b')
        svg.append(f'<text x="{x:.1f}" y="270" font-size="11" text-anchor="middle">{label}</text>')
svg += [f'<text x="970" y="296" font-size="10" text-anchor="end" fill="#8198ad">Updated {today.isoformat()} · Last 31 days</text>','</g></svg>']
Path('assets/activity.svg').write_text('\n'.join(svg)+'\n')

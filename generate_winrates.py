"""
Generates fig:results_winrates — win rates by strategy and color with 95% CI.
Run from monograph/ with: ../.venv/bin/python generate_winrates.py
Output: images/results_winrates.pdf  images/results_winrates.png
"""

import numpy as np
import matplotlib.pyplot as plt

# ── Data from Table tab:results_main ───────────────────────────────────────
# (wins, total)
data = {
    'Crítica':      {'Black': (123, 200), 'White': (124, 200)},
    'Por Fase':     {'Black': ( 89, 200), 'White': ( 72, 200)},
    'Proporcional': {'Black': (103, 200), 'White': (106, 200)},
}

strategies = ['Crítica', 'Por Fase', 'Proporcional']

# y positions: three groups, three dots each (Black / White / Total)
# group spacing = 1.0, within-group spacing = 0.22
GROUP_Y  = {'Crítica': 2.0, 'Por Fase': 1.0, 'Proporcional': 0.0}
OFFSETS  = {'Black': +0.22, 'White': -0.22, 'Total': 0.0}
COLORS   = {'Black': '#222222', 'White': '#888888', 'Total': '#1565C0'}
MARKERS  = {'Black': 'o',       'White': 's',        'Total': 'D'}
SIZES    = {'Black': 7,         'White': 7,           'Total': 9}

fig, ax = plt.subplots(figsize=(7, 4.0))

for strat in strategies:
    d    = data[strat]
    tw   = d['Black'][0] + d['White'][0]
    tn   = d['Black'][1] + d['White'][1]
    vals = {'Black': d['Black'], 'White': d['White'], 'Total': (tw, tn)}

    for cat in ('Black', 'White', 'Total'):
        w, n = vals[cat]
        p       = w / n
        ci_half = 1.96 * np.sqrt(p * (1 - p) / n)
        y       = GROUP_Y[strat] + OFFSETS[cat]

        ax.errorbar(
            p * 100, y,
            xerr=ci_half * 100,
            fmt=MARKERS[cat],
            color=COLORS[cat],
            markersize=SIZES[cat],
            capsize=4, capthick=1.4, elinewidth=1.4,
            zorder=3,
        )

# 50 % reference line
ax.axvline(50, color='#AAAAAA', linestyle='--', linewidth=1.2, zorder=1)

# ── Axes ───────────────────────────────────────────────────────────────────
ax.set_yticks(list(GROUP_Y.values()))
ax.set_yticklabels(strategies, fontsize=11)
ax.set_ylim(-0.65, 2.65)

ax.set_xlabel('Taxa de vitórias (%)', fontsize=11)
ax.set_xlim(24, 78)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0f}%'))

ax.grid(axis='x', linestyle=':', alpha=0.45)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# ── Legend ─────────────────────────────────────────────────────────────────
legend_handles = [
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#222222',
               markersize=7,  label='Black'),
    plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#888888',
               markersize=7,  label='White'),
    plt.Line2D([0], [0], marker='D', color='w', markerfacecolor='#1565C0',
               markersize=9,  label='Total'),
    plt.Line2D([0], [0], color='#AAAAAA', linestyle='--', linewidth=1.2,
               label='Baseline (50%)'),
]
ax.legend(handles=legend_handles, loc='lower right', fontsize=9, framealpha=0.9)

plt.tight_layout()
plt.savefig('images/results_winrates.pdf', bbox_inches='tight')
plt.savefig('images/results_winrates.png', dpi=180, bbox_inches='tight')
print("Saved: images/results_winrates.pdf  images/results_winrates.png")

"""
Generates fig:time_profiles — conceptual time allocation per move for each strategy.
Run from monograph/ with: ../.venv/bin/python generate_time_profiles.py
Output: images/time_profiles.pdf  images/time_profiles.png
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

np.random.seed(7)

BUDGET    = 60.0
N_CONST   = 75
N_MOVES   = 57   # representative game length for one player

moves = np.arange(N_MOVES)
# fill ratio: both players place pieces at similar pace → ~2*i pieces on 225 cells
fill = np.minimum(2 * moves / 225.0, 1.0)


def simulate(n_moves, strategy):
    T_r = BUDGET
    times = []
    for i in range(n_moves):
        N_r = max(1, N_CONST - i)
        base = T_r / N_r

        if strategy == 'flat':
            t = base

        elif strategy == 'proportional':
            rho = fill[i]
            mu  = 0.8 + 0.4 * rho
            t   = mu * base

        elif strategy == 'phase':
            p = fill[i]
            if p < 0.10:
                mu = 1.20
            elif p < 0.45:
                mu = 1.50
            else:
                mu = 0.55
            t = mu * base

        elif strategy == 'critical':
            t = (2.0 if threats[i] else 0.9) * base

        t = max(0.05, min(t, T_r))   # clamp matches BaseTimeManager.clamp; 95% cap is in run_duel.py
        times.append(t)
        T_r -= t
        if T_r <= 0:
            break

    return np.array(times)


# Threats for critical: 16.4% average, concentrated in mid-game
threat_prob = np.where((moves >= 12) & (moves <= 48), 0.24, 0.04)
threats = np.random.random(N_MOVES) < threat_prob

flat_t  = simulate(N_MOVES, 'flat')
prop_t  = simulate(N_MOVES, 'proportional')
phase_t = simulate(N_MOVES, 'phase')
crit_t  = simulate(N_MOVES, 'critical')

# ── Phase boundary vertical lines ──────────────────────────────────────────
# abertura ends at fill=0.10 → i≈11.25; meio ends at fill=0.45 → i≈50.6
BOUNDARY_AB = 11.25
BOUNDARY_MF = 50.6

fig, ax = plt.subplots(figsize=(8, 4.2))

x = np.arange(len(flat_t))

# Shaded phase regions (subtle)
ax.axvspan(0,            BOUNDARY_AB, alpha=0.05, color='#4CAF50', zorder=0)
ax.axvspan(BOUNDARY_AB,  BOUNDARY_MF, alpha=0.05, color='#FF9800', zorder=0)
ax.axvspan(BOUNDARY_MF,  N_MOVES,     alpha=0.05, color='#2196F3', zorder=0)

# Phase labels near top
ymax_label = 1.82
ax.text(5.5,                  ymax_label, 'Abertura',      ha='center', va='top', fontsize=8, color='#555555')
ax.text((BOUNDARY_AB + BOUNDARY_MF) / 2, ymax_label, 'Meio do jogo', ha='center', va='top', fontsize=8, color='#555555')
ax.text((BOUNDARY_MF + N_MOVES) / 2,     ymax_label, 'Final',        ha='center', va='top', fontsize=8, color='#555555')

# Strategy lines
ax.plot(x, flat_t,  label='Flat',         color='#000000', linewidth=2.2, linestyle=(0, (5, 2)), zorder=3)
ax.plot(x, prop_t,  label='Proporcional', color='#2196F3', linewidth=1.8, zorder=3)
ax.plot(x, phase_t, label='Por Fase',     color='#FF9800', linewidth=1.8, zorder=3)
ax.plot(x, crit_t,  label='Crítica',      color='#E53935', linewidth=1.5, alpha=0.9, zorder=3)

# Mark threat spikes on critical line
threat_idx = np.where(threats[:len(crit_t)])[0]
ax.scatter(threat_idx, crit_t[threat_idx],
           color='#E53935', marker='^', s=45, zorder=5)

ax.set_xlabel('Lance do jogador', fontsize=11)
ax.set_ylabel('Tempo alocado (s)', fontsize=11)
ax.set_xlim(0, N_MOVES - 1)
ax.set_ylim(0, 2.0)
ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
ax.grid(axis='y', linestyle=':', alpha=0.45)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('images/time_profiles.pdf', bbox_inches='tight')
plt.savefig('images/time_profiles.png', dpi=180, bbox_inches='tight')
print("Saved: images/time_profiles.pdf  images/time_profiles.png")

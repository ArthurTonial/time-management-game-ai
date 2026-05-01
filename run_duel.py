#!/usr/bin/env python3
"""
run_duel.py — Tournament runner for time-manager strategy comparison.

Usage:
    python run_duel.py --strategy proportional --baseline flat --matches 30 --time-budget 60

Runs N Gomoku matches between two MCTS agents, each controlled by a different
time allocation strategy.  Results are written to results/ as JSON.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from game.gomoku.board import Board
from game.gomoku.gamestate import GameState
from agents.mcts.agent import make_move as mcts_make_move
from time_manager import (
    FlatTimeManager,
    ProportionalTimeManager,
    PhaseTimeManager,
    CriticalTimeManager,
)

STRATEGY_MAP = {
    'flat': FlatTimeManager,
    'proportional': ProportionalTimeManager,
    'phase': PhaseTimeManager,
    'critical': CriticalTimeManager,
}

# Minimum seconds granted per move even when the clock is nearly empty.
MIN_MOVE_TIME = 0.05


def _safe_avg(lst):
    return round(sum(lst) / len(lst), 4) if lst else 0.0


def _color_win_rate(wins_as, played_as, c):
    played = played_as[c]
    return round(wins_as[c] / played, 4) if played > 0 else None


# ---------------------------------------------------------------------------
# Single match
# ---------------------------------------------------------------------------

def run_match(strategy_name, baseline_name, strategy_color, time_budget, verbose=False):
    """
    Play one Gomoku match between two MCTS agents.

    :param strategy_name:  name of the time manager under test
    :param baseline_name:  name of the baseline time manager
    :param strategy_color: 'B' or 'W' — which color the strategy plays
    :param time_budget:    total seconds each player has for the whole game
    :param verbose:        print per-move details
    :return: dict with full match data
    """
    strategy_tm = STRATEGY_MAP[strategy_name]()
    baseline_tm = STRATEGY_MAP[baseline_name]()

    baseline_color = 'W' if strategy_color == 'B' else 'B'
    players = {
        strategy_color: (strategy_tm, strategy_name),
        baseline_color: (baseline_tm, baseline_name),
    }

    time_remaining = {'B': time_budget, 'W': time_budget}
    move_counts = {'B': 0, 'W': 0}
    move_log = []

    state = GameState(Board(), 'B')

    while not state.is_terminal():
        color = state.player
        tm, label = players[color]
        tr = time_remaining[color]
        moves_made = move_counts[color]

        allocated = tm.allocate(tr, moves_made, board=state.get_board(), player=color)
        # Never allocate more than 95 % of remaining budget in one move
        allocated = max(MIN_MOVE_TIME, min(allocated, tr * 0.95))

        t0 = time.time()
        move = mcts_make_move(state, time_limit=allocated)
        spent = time.time() - t0

        time_remaining[color] = max(0.0, tr - spent)
        move_counts[color] += 1

        move_log.append({
            'move_number': len(move_log),
            'player': color,
            'strategy': label,
            'time_allocated': round(allocated, 4),
            'time_spent': round(spent, 4),
            'time_remaining_after': round(time_remaining[color], 4),
            'move': list(move),
        })

        if verbose:
            print(
                f"  [{color}/{label}] move={move}"
                f"  alloc={allocated:.2f}s  spent={spent:.2f}s"
                f"  remaining={time_remaining[color]:.2f}s"
            )

        state = state.next_state(move)

    winner_color = state.winner()  # 'B', 'W', or None (draw)
    winner_strategy = players[winner_color][1] if winner_color is not None else None

    return {
        'strategy_color': strategy_color,
        'winner_color': winner_color,
        'winner_strategy': winner_strategy,
        'move_count': len(move_log),
        'time_remaining_end': time_remaining,
        'moves': move_log,
    }


# ---------------------------------------------------------------------------
# Tournament
# ---------------------------------------------------------------------------

def run_duel(strategy, baseline, n_matches, time_budget, output_dir, color='alternate', verbose=False):
    os.makedirs(output_dir, exist_ok=True)

    strategy_wins = 0
    baseline_wins = 0
    draws = 0
    match_results = []
    strategy_played_as = {'B': 0, 'W': 0}
    strategy_wins_as = {'B': 0, 'W': 0}

    color_label = f" | strategy={color}" if color != 'alternate' else ''
    print(f"\nDuel: {strategy} vs {baseline} | {n_matches} matches | {time_budget}s/player{color_label}\n")

    for i in range(n_matches):
        if color == 'alternate':
            strategy_color = 'B' if i % 2 == 0 else 'W'
        else:
            strategy_color = color
        print(f"Match {i + 1}/{n_matches}  (strategy={strategy_color}) ... ", end='', flush=True)

        match = run_match(strategy, baseline, strategy_color, time_budget, verbose=verbose)
        match['match_id'] = i
        match_results.append(match)

        strategy_played_as[strategy_color] += 1

        ws = match['winner_strategy']
        if ws == strategy:
            strategy_wins += 1
            strategy_wins_as[strategy_color] += 1
            outcome = f"{strategy} wins"
        elif ws == baseline:
            baseline_wins += 1
            outcome = f"{baseline} wins"
        else:
            draws += 1
            outcome = "draw"

        print(f"{outcome}  ({match['move_count']} moves)")

    # Summary statistics
    all_strategy_times = [
        m['time_allocated']
        for r in match_results
        for m in r['moves']
        if m['strategy'] == strategy
    ]
    all_baseline_times = [
        m['time_allocated']
        for r in match_results
        for m in r['moves']
        if m['strategy'] == baseline
    ]

    summary = {
        'strategy': strategy,
        'baseline': baseline,
        'total_matches': n_matches,
        'strategy_wins': strategy_wins,
        'baseline_wins': baseline_wins,
        'draws': draws,
        'strategy_win_rate': round(strategy_wins / n_matches, 4),
        'baseline_win_rate': round(baseline_wins / n_matches, 4),
        'strategy_wins_as_B': strategy_wins_as['B'],
        'strategy_wins_as_W': strategy_wins_as['W'],
        'strategy_matches_as_B': strategy_played_as['B'],
        'strategy_matches_as_W': strategy_played_as['W'],
        'strategy_win_rate_as_B': _color_win_rate(strategy_wins_as, strategy_played_as, 'B'),
        'strategy_win_rate_as_W': _color_win_rate(strategy_wins_as, strategy_played_as, 'W'),
        'avg_time_allocated_strategy': _safe_avg(all_strategy_times),
        'avg_time_allocated_baseline': _safe_avg(all_baseline_times),
    }

    _print_summary(summary)

    output = {
        'config': {
            'strategy': strategy,
            'baseline': baseline,
            'time_budget': time_budget,
            'matches': n_matches,
            'color': color,
            'timestamp': datetime.now().isoformat(),
        },
        'summary': summary,
        'matches': match_results,
    }

    filename = f"{strategy}_vs_{baseline}_{int(time_budget)}s_{color}.json"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved → {filepath}\n")
    return output


def _print_summary(s):
    width = 50
    print(f"\n{'=' * width}")
    print(f"  {s['strategy']:20s}  wins: {s['strategy_wins']:3d} / {s['total_matches']}  ({s['strategy_win_rate'] * 100:.1f}%)")
    print(f"  {s['baseline']:20s}  wins: {s['baseline_wins']:3d} / {s['total_matches']}  ({s['baseline_win_rate'] * 100:.1f}%)")
    print(f"  {'draws':20s}       {s['draws']:3d} / {s['total_matches']}")
    for c, label in (('B', 'Black'), ('W', 'White')):
        n = s[f'strategy_matches_as_{c}']
        if n > 0:
            wr = s[f'strategy_win_rate_as_{c}']
            wins = s[f'strategy_wins_as_{c}']
            print(f"  {s['strategy']} as {label}: {wins}/{n}  ({wr * 100:.1f}%)")
    print(f"  avg move time  {s['strategy']:>15s}: {s['avg_time_allocated_strategy']:.3f}s")
    print(f"  avg move time  {s['baseline']:>15s}: {s['avg_time_allocated_baseline']:.3f}s")
    print(f"{'=' * width}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Run a duel between two MCTS time-manager strategies on Gomoku.'
    )
    parser.add_argument(
        '--strategy', required=True, choices=list(STRATEGY_MAP),
        help='Time manager strategy under test',
    )
    parser.add_argument(
        '--baseline', default='flat', choices=list(STRATEGY_MAP),
        help='Baseline time manager (default: flat)',
    )
    parser.add_argument(
        '--matches', type=int, default=30,
        help='Number of matches (default: 30)',
    )
    parser.add_argument(
        '--time-budget', type=float, default=60.0, dest='time_budget',
        help='Total seconds per player per game (default: 60)',
    )
    parser.add_argument(
        '--output', default='results',
        help='Directory to save results (default: results/)',
    )
    parser.add_argument(
        '--color', default='alternate', choices=['alternate', 'B', 'W'],
        help='Which color the strategy always plays: alternate (default), black, or white',
    )
    parser.add_argument(
        '--verbose', action='store_true',
        help='Print per-move details',
    )

    args = parser.parse_args()
    run_duel(
        strategy=args.strategy,
        baseline=args.baseline,
        n_matches=args.matches,
        time_budget=args.time_budget,
        output_dir=args.output,
        color=args.color,
        verbose=args.verbose,
    )


if __name__ == '__main__':
    main()

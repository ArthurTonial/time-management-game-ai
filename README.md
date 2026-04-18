# Time-Managed Game AI

A research framework for studying how different **time management strategies** affect the performance of MCTS-based game-playing agents in Gomoku.

## Research Goal

This project investigates the following question:

> **How do different per-move time allocation strategies affect the win rate of an MCTS agent in Gomoku, compared to a flat-time baseline?**

### Context

Monte Carlo Tree Search (MCTS) is an **anytime algorithm** — given more thinking time, it generally makes better decisions. In a game with a fixed time budget (e.g., 60 seconds per player), a naive strategy allocates the same fixed time per move. Smarter strategies might allocate more time to critical positions and less to obvious ones.

This project implements a **Time Manager** layer that sits between the game server and the MCTS engine. Before each move, the Time Manager decides how many seconds the agent may think. Different Time Manager implementations represent different strategies.

### Hypothesis

Strategic time allocation (spending more time on complex/critical moves) will result in a higher win rate than a flat-time baseline, because MCTS quality scales directly with thinking time.

### Methodology

- **Game**: Gomoku (15×15, five-in-a-row)
- **Agent under study**: MCTS with a pluggable Time Manager
- **Baseline**: MCTS with a flat time strategy (same N seconds every move)
- **Benchmark**: Each strategy plays a tournament against the flat baseline
- **Metric**: Win rate across N matches (alternating colors to remove first-move bias)

### Time Management Strategies (planned)

| Strategy | Description |
|----------|-------------|
| `flat` | Always allocate the same fixed time per move (baseline) |
| `proportional` | Allocate based on remaining time / estimated remaining moves |
| `phase` | Allocate more time in the midgame, less in opening/endgame |
| `critical` | Detect threatening positions and allocate more time |
| `adaptive` | Combine tree uncertainty and game phase signals |

## Features

- **Focused Game**: Gomoku (15×15, Five-in-a-Row)
- **Pluggable Time Manager**: Swap allocation strategies without changing the MCTS core
- **Time-budget-driven MCTS**: Agent runs until clock expires, not a fixed iteration count
- **Competitive Benchmarks**: Each strategy evaluated against the flat baseline in a tournament
- **Detailed Analytics**: Match history, per-move timing, and win-rate statistics

## Research

This project is an undergraduate thesis (TCC) on time management for game-playing AI.

**Core reference papers** (see `docs/`):
- *A Survey of Monte Carlo Tree Search Methods* — Browne et al.
- *Monte Carlo Algorithms for Time-Constrained General Game Playing*
- *Time Management for Monte Carlo Tree Search* (applied to Go)

**Key insight from literature**: MCTS performance is highly sensitive to time allocation. Papers on Go have shown that non-uniform time strategies (spending more on critical junctures) can significantly improve win rate versus flat allocation.

This project applies and benchmarks those ideas on Gomoku.

## Requirements

- Python 3.7+
- No external dependencies required for core functionality
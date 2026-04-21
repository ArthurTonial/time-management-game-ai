# Project TODO

Ordered list of work items. Check off as you go. Each section is a phase — complete them in order.

---

## Phase 1 — Clean Up & Commit What Exists

- [x] Commit staged MCTS files (`agent.py`, `mcts.py`, `mcts_node.py`)
- [x] Commit Minimax files (`src/agents/minimax/`)
- [x] Commit `README.md` and `TODO.md` updates
- [x] Fix `gomoku/board.py`: rename `_is_full()` → `is_full()` and commit

---

## Phase 2 — Switch MCTS to Time-Budget Mode

Right now MCTS runs for a fixed number of iterations (10,000). For the thesis, it must run until a **time budget expires**.

- [x] Rewrite `src/agents/mcts/mcts.py`: replace iteration loop with a `while time.time() < deadline` loop
- [x] Update `src/agents/mcts/agent.py`: accept a `time_limit` parameter instead of `iterations`
- [x] Verify: running for 1s vs 5s produces noticeably different move quality

---

## Phase 3 — Implement the Time Manager Layer

The Time Manager is a new component that wraps the MCTS agent. It receives:

- Total time budget remaining for the player
- Move number (game phase)
- Optionally: board state (for critical move detection)

And it returns: **seconds to allocate for this move**.

### Directory structure to create

```
src/
  time_manager/
    base.py         # Abstract base class / interface
    flat.py         # Baseline: always return budget / estimated_moves_remaining
    proportional.py # Remaining time / estimated remaining moves
    phase.py        # Opening/midgame/endgame phases with different weights
    critical.py     # Detect threats (4-in-a-row, forced responses) → more time
```

- [x] Create `src/time_manager/base.py` with abstract interface
- [x] Implement `flat.py` (the baseline — must be done first)
- [x] Implement `proportional.py`
- [x] Implement `phase.py`
- [x] Implement `critical.py` (hardest — needs board threat detection)

---

## Phase 4 — Build the Tournament Runner (`run_duel.py`)

It needs to:

- Accept a strategy name (e.g., `--strategy proportional`) and a baseline name
- Run N matches, alternating colors
- Collect per-match results (winner, move count, per-move time used)
- Print a summary table: wins, losses, draws, avg move time

- [x] Create `run_duel.py` skeleton (calls `server.py` N times)
- [x] Add `--strategy` and `--baseline` arguments
- [x] Add results aggregation and summary output
- [x] Write results to `results/` as JSON or CSV

---

## Phase 5 — Run Experiments & Collect Data

Define a reproducible experiment matrix:

| Strategy | Time Budget | Matches per pairing |
| -------- | ----------- | ------------------- |
| flat vs flat | 60s | 30 |
| proportional vs flat | 60s | 30 |
| phase vs flat | 60s | 30 |
| critical vs flat | 60s | 30 |

- [ ] Run each pairing in the matrix
- [ ] Save results to `results/` with clear filenames (e.g., `proportional_vs_flat_60s.json`)
- [ ] Compute win rates and confidence intervals

---

## Phase 6 — Analysis & Write-Up

- [ ] Plot win rate per strategy (bar chart or table)
- [ ] Plot avg thinking time per move per strategy
- [ ] Analyze: do strategies spend more time on "critical" moves? Does it pay off?
- [ ] Write thesis chapters based on findings

---

## Backlog (nice-to-have, not blocking)

- [ ] Add `tests/` unit tests for board logic and time manager calculations
- [ ] Improve Gomoku threat detection for use in `critical.py`
- [ ] Add move-timing output to match history files
- [ ] Visualize a game replay from `history.txt`

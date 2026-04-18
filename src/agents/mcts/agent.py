"""
MCTS Agent — time-budget mode.
"""
import time
from typing import Tuple
from .mcts import mcts_search

DEFAULT_TIME_LIMIT = 1.0  # seconds per move

def make_move(state, time_limit: float = DEFAULT_TIME_LIMIT) -> Tuple[int, int]:
    """
    Returns a move using MCTS within the given time budget.

    :param state: current game state
    :param time_limit: seconds allowed for this move
    :return: (x, y) coordinates of the chosen move
    """
    legal_moves = list(state.legal_moves())

    if not legal_moves:
        raise ValueError("No legal moves available")

    if len(legal_moves) == 1:
        return legal_moves[0]

    print(f"  Thinking for {time_limit:.1f}s ({len(legal_moves)} legal moves)...")
    start = time.time()

    move = mcts_search(state, time_limit=time_limit)

    elapsed = time.time() - start
    print(f"  Decision made in {elapsed:.2f}s")

    return move if move is not None else legal_moves[0]

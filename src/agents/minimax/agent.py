"""
Minimax Agent with Alpha-Beta Pruning
"""
import time
from typing import Tuple
from .minimax import minimax_move, simple_gomoku_eval


def make_move(state) -> Tuple[int, int]:
    legal_moves = list(state.legal_moves())

    if not legal_moves:
        raise ValueError("No legal moves available")
    if len(legal_moves) == 1:
        return legal_moves[0]

    game_name = getattr(state, 'game_name', 'Unknown')

    if game_name == 'Gomoku':
        eval_func = simple_gomoku_eval
        move_gen = _gomoku_move_generator
        pieces = sum(
            1 for r in range(state.get_board().size)
            for c in range(state.get_board().size)
            if state.get_board().board[r][c] != '.'
        )
        depth = 4 if pieces >= 6 else 3
    else:
        eval_func = _default_eval
        move_gen = None
        depth = 4

    print(f"  Thinking with Minimax depth {depth} ({len(legal_moves)} legal moves)...")
    start = time.time()
    move = minimax_move(state, max_depth=depth, eval_func=eval_func, move_generator=move_gen)
    print(f"  Decision made in {time.time() - start:.2f}s")
    return move


# ------------------------------------------------------------------
# Gomoku-specific helpers
# ------------------------------------------------------------------

def _expand_cell(board, row: int, col: int, radius: int, out: set) -> None:
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            nr, nc = row + dr, col + dc
            if board.is_empty(nr, nc):
                out.add((nc, nr))


def _gomoku_candidates(state, radius: int = 2) -> set:
    """
    Return empty cells within `radius` of any occupied cell.
    Falls back to the board centre on an empty board.
    """
    board = state.get_board()
    grid = board.board
    size = board.size
    candidates: set = set()

    for r in range(size):
        for c in range(size):
            if grid[r][c] != board.EMPTY:
                _expand_cell(board, r, c, radius, candidates)

    if not candidates:
        mid = size // 2
        return {(mid, mid)}

    return candidates


def _order_candidates(candidates, state) -> list:
    """
    Sort candidates by neighbourhood density (most surrounded = first),
    so alpha-beta sees promising moves early and prunes more aggressively.
    """
    board = state.get_board()
    grid = board.board
    size = board.size

    def density(move):
        x, y = move  # (col, row)
        return sum(
            1
            for dr in range(-1, 2)
            for dc in range(-1, 2)
            if (dr or dc)
            and 0 <= y + dr < size
            and 0 <= x + dc < size
            and grid[y + dr][x + dc] != '.'
        )

    return sorted(candidates, key=density, reverse=True)


def _gomoku_move_generator(state) -> list:
    return _order_candidates(_gomoku_candidates(state, radius=1), state)


# ------------------------------------------------------------------
# Fallback evaluation for non-Gomoku games
# ------------------------------------------------------------------

def _default_eval(state, player: str) -> float:
    if state.is_terminal():
        winner = state.winner()
        if winner == player:
            return 10000
        elif winner is not None:
            return -10000
        return 0

    if hasattr(state.board, 'num_pieces'):
        opponent = 'W' if player == 'B' else 'B'
        return state.board.num_pieces(player) - state.board.num_pieces(opponent)

    return 0

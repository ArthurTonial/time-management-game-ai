import math
from typing import Tuple, Callable, Optional


def minimax_move(
    state,
    max_depth: int,
    eval_func: Callable,
    move_generator: Optional[Callable] = None,
) -> Tuple[int, int]:
    """
    Returns a move computed by minimax with alpha-beta pruning.

    :param state:          current game state
    :param max_depth:      maximum search depth (-1 = unlimited)
    :param eval_func:      evaluation function (state, player) -> float
    :param move_generator: optional callable (state) -> iterable of moves;
                           defaults to state.legal_moves()
    :return: (x, y) coordinates
    """
    moves = list(move_generator(state) if move_generator else state.legal_moves())

    if not moves:
        raise ValueError("No legal moves available")
    if len(moves) == 1:
        return moves[0]

    best_move = moves[0]
    best_value = -math.inf
    current_player = state.player
    alpha = -math.inf
    beta = math.inf

    for move in moves:
        next_state = state.next_state(move)
        value = _minimax_core(
            next_state,
            max_depth - 1 if max_depth != -1 else -1,
            alpha, beta,
            True,
            current_player,
            eval_func,
            move_generator,
        )
        if value > best_value:
            best_value = value
            best_move = move
        alpha = max(alpha, best_value)
        if beta <= alpha:
            break

    return best_move


def _minimax_core(
    state,
    depth: int,
    alpha: float,
    beta: float,
    is_maximizing: bool,
    original_player: str,
    eval_func: Callable,
    move_generator: Optional[Callable],
) -> float:
    if state.is_terminal() or depth == 0:
        return eval_func(state, original_player)

    best_eval = -math.inf if is_maximizing else math.inf

    for move in (move_generator(state) if move_generator else state.legal_moves()):
        next_state = state.next_state(move)
        score = _minimax_core(
            next_state, depth - 1, alpha, beta,
            not is_maximizing, original_player, eval_func, move_generator,
        )
        if is_maximizing:
            best_eval = max(best_eval, score)
            alpha = max(alpha, score)
        else:
            best_eval = min(best_eval, score)
            beta = min(beta, score)
        if beta <= alpha:
            break

    return best_eval


def simple_gomoku_eval(state, player: str) -> float:
    board = state.get_board()
    if state.is_terminal():
        winner = state.winner()
        if winner == player:
            return 10000
        elif winner is not None:
            return -10000
        return 0

    player_score = count_patterns(board, player)
    opponent_score = count_patterns(board, board.opponent(player))
    return player_score - opponent_score


def count_patterns(board, player: str) -> float:
    """
    Score consecutive runs of `player` pieces, weighted by length and openness.
    Each run is counted exactly once by starting only at the first cell of that run.
    """
    score = 0
    grid = board.board
    size = board.size
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    pattern_weights = {2: 10, 3: 100, 4: 1000, 5: 10000}

    for row in range(size):
        for col in range(size):
            if grid[row][col] != player:
                continue
            for dr, dc in directions:
                # Only process the start of each run to avoid double-counting
                prev_r, prev_c = row - dr, col - dc
                if (
                    0 <= prev_r < size
                    and 0 <= prev_c < size
                    and grid[prev_r][prev_c] == player
                ):
                    continue

                # Measure run length
                count = 0
                r, c = row, col
                while 0 <= r < size and 0 <= c < size and grid[r][c] == player:
                    count += 1
                    r += dr
                    c += dc

                if count < 2:
                    continue

                end_r, end_c = r, c
                start_open = (
                    0 <= prev_r < size and 0 <= prev_c < size
                    and grid[prev_r][prev_c] == board.EMPTY
                )
                end_open = (
                    0 <= end_r < size and 0 <= end_c < size
                    and grid[end_r][end_c] == board.EMPTY
                )
                multiplier = 2 if (start_open and end_open) else 1.5 if (start_open or end_open) else 1

                if count in pattern_weights:
                    score += pattern_weights[count] * multiplier

    return score

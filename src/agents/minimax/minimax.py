import random
from typing import Tuple, Callable
import math


def minimax_move(state, max_depth: int, eval_func: Callable) -> Tuple[int, int]:
    """
    Returns a move computed by the minimax algorithm with alpha-beta pruning for the given game state.
    :param state: state to make the move (instance of GameState)
    :param max_depth: maximum depth of search (-1 = unlimited)
    :param eval_func: the function to evaluate a terminal or leaf state (when search is interrupted at max_depth)
                    This function should take a GameState object and a string identifying the player,
                    and should return a float value representing the utility of the state for the player.
    :return: (int, int) tuple with x, y coordinates of the move (remember: 0 is the first row/column)
    """
    
    # Get all legal moves
    legal_moves = list(state.legal_moves())
    
    if not legal_moves:
        raise ValueError("No legal moves available")
    
    # If only one legal move, return it immediately
    if len(legal_moves) == 1:
        return legal_moves[0]
    
    # Initialize best move and best value
    best_move = legal_moves[0]
    best_value = -math.inf
    current_player = state.player
    
    # Alpha-beta pruning initialization
    alpha = -math.inf
    beta = math.inf
    
    # Try each legal move
    for move in legal_moves:
        # Generate the next state
        next_state = state.next_state(move)
        
        # Get the minimax value for this move
        move_value = _minimax_core(
            next_state, 
            max_depth - 1 if max_depth != -1 else -1,
            alpha, 
            beta, 
            True, 
            current_player, 
            eval_func
        )
        
        # Update best move if this move is better
        if move_value > best_value:
            best_value = move_value
            best_move = move
        
        # Update alpha for pruning
        alpha = max(alpha, best_value)
        
        # Alpha-beta pruning
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
        eval_func: Callable) -> float:
    """
    Core minimax logic with alpha-beta pruning
    :param state: current game state
    :param depth: remaining depth to search
    :param alpha: alpha value for pruning
    :param beta: beta value for pruning
    :param is_maximizing: True for maximizing player, False for minimizing player
    :param original_player: the player who called the original minimax_move
    :param eval_func: evaluation function
    :return: evaluation value of the state
    """
    # Terminal state or maximum depth reached
    if state.is_terminal() or depth == 0:
        return eval_func(state, original_player)
    
    # Initialize best value based on player type
    best_eval = -math.inf if is_maximizing else math.inf
    
    for move in state.legal_moves():
        next_state = state.next_state(move)
        eval_score = _minimax_core(next_state, depth - 1, alpha, beta, not is_maximizing, original_player, eval_func)
        
        if is_maximizing:
            best_eval = max(best_eval, eval_score)
            alpha = max(alpha, eval_score)
        else:
            best_eval = min(best_eval, eval_score)
            beta = min(beta, eval_score)
        
        # Alpha-beta pruning
        if beta <= alpha:
            break
    
    return best_eval


def simple_gomoku_eval(state, player: str) -> float:
    """
    Simple evaluation function for Gomoku.
    This function evaluates the board position for the given player.
    :param state: GameState object
    :param player: player to evaluate for ('B' or 'W')
    :return: evaluation score (higher is better for the player)
    """
    board = state.get_board()
    
    # If game is over, return definitive scores
    if state.is_terminal():
        winner = state.winner()
        if winner == player:
            return 10000  # Win
        elif winner is not None:
            return -10000  # Loss
        else:
            return 0  # Draw
    
    # Count patterns for both players
    player_score = count_patterns(board, player)
    opponent = board.opponent(player)
    opponent_score = count_patterns(board, opponent)
    
    return player_score - opponent_score


def count_patterns(board, player: str) -> float:
    """
    Count various patterns (lines of 2, 3, 4) for the given player
    :param board: Board object
    :param player: player color ('B' or 'W')
    :return: weighted score based on patterns
    """
    score = 0
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # horizontal, vertical, diagonals
    
    # Weights for different pattern lengths
    pattern_weights = {
        2: 10,
        3: 100,
        4: 1000,
        5: 10000  # This shouldn't happen in non-terminal states, but just in case
    }
    
    for row in range(board.size):
        for col in range(board.size):
            if board.board[row][col] == player:
                for dr, dc in directions:
                    # Count consecutive pieces in this direction
                    count = 1
                    r, c = row + dr, col + dc
                    
                    # Count forward
                    while (0 <= r < board.size and 0 <= c < board.size and 
                           board.board[r][c] == player):
                        count += 1
                        r += dr
                        c += dc
                    
                    # Don't count backwards to avoid double counting
                    # Just check if the line is "open" (has empty spaces on ends)
                    if count >= 2:
                        # Check if the pattern is open on both ends
                        start_r, start_c = row - dr, col - dc
                        end_r, end_c = r, c
                        
                        start_open = (0 <= start_r < board.size and 0 <= start_c < board.size and 
                                    board.board[start_r][start_c] == board.EMPTY)
                        end_open = (0 <= end_r < board.size and 0 <= end_c < board.size and 
                                  board.board[end_r][end_c] == board.EMPTY)
                        
                        # Bonus for open patterns
                        multiplier = 1
                        if start_open and end_open:
                            multiplier = 2  # Both ends open
                        elif start_open or end_open:
                            multiplier = 1.5  # One end open
                        
                        if count in pattern_weights:
                            score += pattern_weights[count] * multiplier
    
    return score
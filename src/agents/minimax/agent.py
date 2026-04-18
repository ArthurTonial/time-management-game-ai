"""
Minimax Agent with Alpha-Beta Pruning
"""
from typing import Tuple
from .minimax import minimax_move, simple_gomoku_eval

def make_move(state) -> Tuple[int, int]:
    """
    Returns a move using Minimax with alpha-beta pruning.
    
    :param state: current game state
    :return: (int, int) tuple with x, y coordinates of the move
    """
    import time
    
    # Get all legal moves
    legal_moves = list(state.legal_moves())
    
    if not legal_moves:
        raise ValueError("No legal moves available")
    
    # If only one legal move, return it immediately
    if len(legal_moves) == 1:
        return legal_moves[0]
    
    print(f"  Thinking with Minimax depth 4 ({len(legal_moves)} legal moves)...")
    start_time = time.time()
    
    # Determine which evaluation function to use based on game type
    game_name = state.game_name if hasattr(state, 'game_name') else 'Unknown'
    
    if game_name == 'Gomoku':
        eval_func = simple_gomoku_eval
    else:
        # Default simple evaluation for other games
        eval_func = lambda s, p: _default_eval(s, p)
    
    # Use Minimax with depth 4
    move = minimax_move(state, max_depth=4, eval_func=eval_func)
    
    elapsed = time.time() - start_time
    print(f"  Decision made in {elapsed:.2f}s")
    
    return move


def _default_eval(state, player: str) -> float:
    """
    Default evaluation function for games without specific evaluation.
    Returns 0 for non-terminal states, and win/loss/draw values for terminal states.
    """
    if state.is_terminal():
        winner = state.winner()
        if winner == player:
            return 10000  # Win
        elif winner is not None:
            return -10000  # Loss
        else:
            return 0  # Draw
    
    # For non-terminal states, try to use piece count if available
    if hasattr(state.board, 'num_pieces'):
        # For games like Othello
        player_pieces = state.board.num_pieces(player)
        opponent = 'W' if player == 'B' else 'B'
        opponent_pieces = state.board.num_pieces(opponent)
        return player_pieces - opponent_pieces
    
    return 0  # Neutral evaluation if nothing else works
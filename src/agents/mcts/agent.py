"""
High Complexity MCTS Agent - 10,000 iterations per move
"""
from typing import Tuple
from .mcts import mcts_search

def make_move(state) -> Tuple[int, int]:
    """
    Returns a move using MCTS with 10,000 iterations for deep search.
    
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
    
    print(f"  Thinking with 10,000 iterations ({len(legal_moves)} legal moves)...")
    start_time = time.time()
    
    # Use MCTS with 10,000 iterations for very deep search
    root = mcts_search(state, max_iterations=10000)
    
    elapsed = time.time() - start_time
    print(f"  Decision made in {elapsed:.2f}s")
    
    if root is not None:
        return root
    else:
        # Fallback to first legal move if MCTS fails
        return legal_moves[0]

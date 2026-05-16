from .base import BaseTimeManager, _DEFAULT_ESTIMATED_MOVES


class ProportionalTimeManager(BaseTimeManager):
    """
    Proportional strategy: estimate moves remaining from the actual board state
    (empty cells / 2) rather than a fixed constant.

    When a board is available the denominator shrinks as pieces are placed,
    so allocation per move grows naturally as the game progresses.  This
    differs from FlatTimeManager, which always divides by (constant - move_number)
    regardless of what is actually on the board.

    Falls back to flat behaviour when board=None.
    """

    def __init__(self, estimated_total_moves: int = _DEFAULT_ESTIMATED_MOVES):
        self.estimated_total_moves = estimated_total_moves

    def allocate(self, time_remaining: float, move_number: int, board=None, player: str = None) -> float:
        if board is not None:
            empty_cells = sum(cell == '.' for row in board.board for cell in row)
            moves_remaining = max(1, empty_cells // 2)
        else:
            moves_remaining = max(1, self.estimated_total_moves - move_number)
        allocation = time_remaining / moves_remaining
        return self.clamp(allocation, 0.05, time_remaining)

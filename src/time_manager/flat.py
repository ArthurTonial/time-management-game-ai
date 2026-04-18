from .base import BaseTimeManager, _DEFAULT_ESTIMATED_MOVES


class FlatTimeManager(BaseTimeManager):
    """
    Baseline strategy: divide the remaining clock equally across all
    estimated future moves.  Every move receives the same slice regardless
    of board position or game phase.

    allocation = time_remaining / estimated_moves_remaining
    """

    def __init__(self, estimated_total_moves: int = _DEFAULT_ESTIMATED_MOVES):
        """
        :param estimated_total_moves: total moves expected per player per game
        """
        self.estimated_total_moves = estimated_total_moves

    def allocate(self, time_remaining: float, move_number: int, board=None, player: str = None) -> float:
        moves_remaining = max(1, self.estimated_total_moves - move_number)
        allocation = time_remaining / moves_remaining
        return self.clamp(allocation, 0.05, time_remaining)

from .base import BaseTimeManager, _DEFAULT_ESTIMATED_MOVES


class ProportionalTimeManager(BaseTimeManager):
    """
    Proportional strategy: spend a fixed fraction of the *remaining* clock
    on each move, so time spent per move shrinks naturally as the game goes on.

    allocation = time_remaining / moves_remaining

    Compared to FlatTimeManager this is identical in the first move, but
    self-corrects if the clock drains faster or slower than expected —
    the denominator always reflects how many moves are left, not a fixed
    global estimate.
    """

    def __init__(self, estimated_total_moves: int = _DEFAULT_ESTIMATED_MOVES):
        self.estimated_total_moves = estimated_total_moves

    def allocate(self, time_remaining: float, move_number: int, board=None, player: str = None) -> float:
        moves_remaining = max(1, self.estimated_total_moves - move_number)
        allocation = time_remaining / moves_remaining
        return self.clamp(allocation, 0.05, time_remaining)

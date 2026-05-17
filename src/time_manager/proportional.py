from .base import BaseTimeManager, _DEFAULT_ESTIMATED_MOVES


class ProportionalTimeManager(BaseTimeManager):
    """
    Proportional strategy: uses the same calibrated denominator as FlatTimeManager
    but scales the allocation up as the board fills.

    The multiplier rises linearly from 0.8× at an empty board to 1.2× when the
    board is full, so early moves are slightly conservative and late moves get
    extra time — matching Gomoku's growing tactical complexity as pieces cluster.
    The 0.8–1.2 range is centred on 1.0, keeping the average close to flat.

    allocation = (time_remaining / moves_remaining) * (0.8 + 0.4 * fill_ratio)
    """

    _SCALE_MIN = 0.8   # multiplier at empty board
    _SCALE_MAX = 1.2   # multiplier at full board

    def __init__(self, estimated_total_moves: int = _DEFAULT_ESTIMATED_MOVES):
        self.estimated_total_moves = estimated_total_moves

    def allocate(self, time_remaining: float, move_number: int, board=None, player: str = None) -> float:
        moves_remaining = max(1, self.estimated_total_moves - move_number)
        flat = time_remaining / moves_remaining

        if board is not None:
            empty_cells = sum(cell == '.' for row in board.board for cell in row)
            fill_ratio = 1.0 - empty_cells / board.size ** 2
            multiplier = self._SCALE_MIN + (self._SCALE_MAX - self._SCALE_MIN) * fill_ratio
        else:
            multiplier = 1.0

        return self.clamp(flat * multiplier, 0.05, time_remaining)

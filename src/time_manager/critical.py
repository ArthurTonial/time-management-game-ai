from .base import BaseTimeManager, _DEFAULT_ESTIMATED_MOVES

# How much extra time to grant when a threat is detected.
# A multiplier of 2.0 means "spend twice the flat allocation".
_THREAT_MULTIPLIER = 2.0
_NORMAL_MULTIPLIER = 0.9   # slightly below flat to compensate on average

# A "threat" is defined as N or more pieces in a row with open ends.
_THREAT_LENGTH = 4          # four-in-a-row is an immediate winning threat


class CriticalTimeManager(BaseTimeManager):
    """
    Threat-aware strategy: detects whether the current position contains a
    critical threat (4-in-a-row for either player) and doubles the time
    allocation.  On non-critical moves it spends slightly less than flat
    to keep the overall budget balanced.

    allocation = (time_remaining / moves_remaining) * multiplier
    where multiplier = _THREAT_MULTIPLIER if threat else _NORMAL_MULTIPLIER
    """

    def __init__(self, estimated_total_moves: int = _DEFAULT_ESTIMATED_MOVES):
        self.estimated_total_moves = estimated_total_moves

    # ------------------------------------------------------------------
    # Threat detection
    # ------------------------------------------------------------------

    @staticmethod
    def _count_in_direction(board_grid, size, row, col, dr, dc, player):
        count = 0
        r, c = row, col
        while 0 <= r < size and 0 <= c < size and board_grid[r][c] == player:
            count += 1
            r += dr
            c += dc
        return count

    @staticmethod
    def _end_is_open(grid, size, r, c):
        return 0 <= r < size and 0 <= c < size and grid[r][c] == "."

    @staticmethod
    def _direction_has_open_threat(grid, size, r, c, dr, dc, target, length):
        fwd = CriticalTimeManager._count_in_direction(grid, size, r, c, dr, dc, target)
        if fwd < length:
            return False
        return (
            CriticalTimeManager._end_is_open(grid, size, r + dr * fwd, c + dc * fwd)
            or CriticalTimeManager._end_is_open(grid, size, r - dr, c - dc)
        )

    @staticmethod
    def _target_has_threat(grid, size, target, directions, length):
        for r in range(size):
            for c in range(size):
                if grid[r][c] != target:
                    continue
                for dr, dc in directions:
                    if CriticalTimeManager._direction_has_open_threat(grid, size, r, c, dr, dc, target, length):
                        return True
        return False

    def _has_threat(self, board, player: str, length: int = _THREAT_LENGTH) -> bool:
        """Return True if player or opponent has an open threat of `length` in a row."""
        grid = board.board
        size = board.size
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        opponent = "W" if player == "B" else "B"
        return (
            self._target_has_threat(grid, size, player, directions, length)
            or self._target_has_threat(grid, size, opponent, directions, length)
        )

    # ------------------------------------------------------------------
    # Allocation
    # ------------------------------------------------------------------

    def allocate(self, time_remaining: float, move_number: int, board=None, player: str = None) -> float:
        # Use the same denominator as FlatTimeManager so threat multipliers are meaningful.
        # Board is only consulted for threat detection.
        moves_remaining = max(1, self.estimated_total_moves - move_number)
        flat = time_remaining / moves_remaining

        if board is not None and player is not None and self._has_threat(board, player):
            multiplier = _THREAT_MULTIPLIER
        else:
            multiplier = _NORMAL_MULTIPLIER

        return self.clamp(flat * multiplier, 0.05, time_remaining)

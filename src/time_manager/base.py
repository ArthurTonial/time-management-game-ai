from abc import ABC, abstractmethod

# Gomoku on a 15×15 board: each player makes at most ~112 moves (225 cells / 2).
# We use a conservative estimate so we never starve late-game moves.
_DEFAULT_ESTIMATED_MOVES = 100

class BaseTimeManager(ABC):
    """
    Abstract interface for per-move time allocation strategies.

    All strategies receive the current game context and return the number of
    seconds the MCTS agent should spend on the next move.
    """

    @abstractmethod
    def allocate(
        self,
        time_remaining: float,
        move_number: int,
        board=None,
        player: str = None,
    ) -> float:
        """
        Decide how many seconds to spend on the current move.

        :param time_remaining: total clock seconds left for this player
        :param move_number:    how many moves this player has already made (0-indexed)
        :param board:          current Board object (optional — used by threat-aware strategies)
        :param player:         current player colour, e.g. 'B' or 'W' (optional)
        :return:               seconds to allocate (must be > 0 and <= time_remaining)
        """

    # ------------------------------------------------------------------
    # Shared utility
    # ------------------------------------------------------------------

    @staticmethod
    def clamp(value: float, minimum: float, time_remaining: float) -> float:
        """Return value clamped to [minimum, time_remaining]."""
        return max(minimum, min(value, time_remaining))

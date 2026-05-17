from .base import BaseTimeManager, _DEFAULT_ESTIMATED_MOVES

# Multipliers relative to the flat allocation for each game phase.
# opening: slight boost for foundational positioning
# midgame: peak tactical complexity — spend the most here
# endgame: positions become more forcing; budget was already used in midgame
_PHASE_WEIGHTS = {
    "opening": 1.2,
    "midgame": 1.5,
    "endgame": 0.55,
}

# Calibrated from empirical data (avg game: 52 moves/player, board fill 46% at end):
# opening  = first ~12 moves/player  (board 0–10% filled)
# midgame  = moves 12–40+/player     (board 10–45% filled; 57% of games reach endgame)
# endgame  = moves 40+/player        (board 45%+ filled)
# Previously 0.25/0.70 — 0.70 was never reached in any observed game.
_OPENING_CUTOFF = 0.10
_ENDGAME_CUTOFF = 0.45


class PhaseTimeManager(BaseTimeManager):
    """
    Phase-aware strategy: applies a multiplier to the flat allocation
    depending on whether we are in the opening, midgame, or endgame.

    allocation = (time_remaining / moves_remaining) * phase_weight
    """

    def __init__(
        self,
        estimated_total_moves: int = _DEFAULT_ESTIMATED_MOVES,
        phase_weights: dict = None,
    ):
        self.estimated_total_moves = estimated_total_moves
        self.weights = phase_weights or _PHASE_WEIGHTS

    def _phase_from_progress(self, progress: float) -> str:
        if progress < _OPENING_CUTOFF:
            return "opening"
        elif progress < _ENDGAME_CUTOFF:
            return "midgame"
        return "endgame"

    def allocate(self, time_remaining: float, move_number: int, board=None, player: str = None) -> float:
        # Use the same denominator as FlatTimeManager so the weight is meaningful.
        # Board is only consulted for progress tracking (phase classification).
        moves_remaining = max(1, self.estimated_total_moves - move_number)
        if board is not None:
            empty_cells = sum(cell == '.' for row in board.board for cell in row)
            total_cells = board.size ** 2
            progress = 1.0 - empty_cells / total_cells
        else:
            progress = move_number / max(1, self.estimated_total_moves)
        flat = time_remaining / moves_remaining
        weight = self.weights[self._phase_from_progress(progress)]
        return self.clamp(flat * weight, 0.05, time_remaining)

from .base import BaseTimeManager, _DEFAULT_ESTIMATED_MOVES

# Multipliers relative to the flat allocation for each game phase.
# opening: save time early (pieces are spread, threats are few)
# midgame: spend more (tactical complexity peaks)
# endgame: spend less (fewer moves left, position is clearer)
_PHASE_WEIGHTS = {
    "opening": 0.75,
    "midgame": 1.5,
    "endgame": 0.75,
}

_OPENING_CUTOFF = 0.25   # first 25% of estimated moves
_ENDGAME_CUTOFF = 0.70   # last 30% of estimated moves


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
        if board is not None:
            empty_cells = sum(cell == '.' for row in board.board for cell in row)
            total_cells = board.size ** 2
            moves_remaining = max(1, empty_cells // 2)
            progress = 1.0 - empty_cells / total_cells
        else:
            moves_remaining = max(1, self.estimated_total_moves - move_number)
            progress = move_number / max(1, self.estimated_total_moves)
        flat = time_remaining / moves_remaining
        weight = self.weights[self._phase_from_progress(progress)]
        return self.clamp(flat * weight, 0.05, time_remaining)

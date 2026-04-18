from .base import BaseTimeManager, _DEFAULT_ESTIMATED_MOVES

# Multipliers relative to the flat allocation for each game phase.
# opening: save time early (pieces are spread, threats are few)
# midgame: spend more (tactical complexity peaks)
# endgame: spend less (fewer moves left, position is clearer)
_PHASE_WEIGHTS = {
    "opening": 0.6,
    "midgame": 1.4,
    "endgame": 0.8,
}

_OPENING_CUTOFF = 0.20   # first 20% of estimated moves
_ENDGAME_CUTOFF = 0.75   # last 25% of estimated moves


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

    def _phase(self, move_number: int) -> str:
        progress = move_number / max(1, self.estimated_total_moves)
        if progress < _OPENING_CUTOFF:
            return "opening"
        elif progress < _ENDGAME_CUTOFF:
            return "midgame"
        return "endgame"

    def allocate(self, time_remaining: float, move_number: int, board=None, player: str = None) -> float:
        moves_remaining = max(1, self.estimated_total_moves - move_number)
        flat = time_remaining / moves_remaining
        weight = self.weights[self._phase(move_number)]
        return self.clamp(flat * weight, 0.05, time_remaining)

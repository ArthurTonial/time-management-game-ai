import math
import random

WIN_VALUE = 1.0
LOSS_VALUE = 0.0
DRAW_VALUE = 0.5


class MCTSNode:
    def __init__(self, state, parent=None, action=None, player=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.player = state.player
        self.children = []
        self.visits = 0
        self.wins = 0.0

        if state.player is not None:
            self.untried_actions = list(state.legal_moves())
            random.shuffle(self.untried_actions)
        else:
            self.untried_actions = []

    def is_terminal(self) -> bool:
        return self.state.is_terminal()

    def is_fully_expanded(self) -> bool:
        return len(self.untried_actions) == 0

    def expand(self):
        if not self.untried_actions:
            return None
        action = self.untried_actions.pop()
        next_state = self.state.next_state(action)
        child_node = MCTSNode(next_state, parent=self, action=action)
        self.children.append(child_node)
        return child_node

    def best_child(self, c: float = math.sqrt(2)):
        if not self.children:
            return None

        def ucb1(child):
            exploit = 1.0 - child.wins / child.visits
            explore = c * math.sqrt(math.log(self.visits) / child.visits)
            return exploit + explore

        best_score = max(ucb1(child) for child in self.children)
        tied = [child for child in self.children if ucb1(child) == best_score]
        return random.choice(tied)

    # ------------------------------------------------------------------
    # Rollout
    # ------------------------------------------------------------------

    @staticmethod
    def _biased_choice(actions, state, radius: int = 5):
        """
        Prefer moves near the last placed piece.
        Falls back to a uniform random pick when the board is empty or the
        neighbourhood is exhausted.
        """
        board = state.board
        last = getattr(board, 'last_move', None)
        if last is not None:
            lr, lc, _ = last  # last_move = (row, col, player)
            nearby = [
                (x, y) for (x, y) in actions
                if abs(y - lr) <= radius and abs(x - lc) <= radius
            ]
            if nearby:
                return random.choice(nearby)
        return random.choice(actions)

    def rollout(self):
        current_state = self.state.copy()
        original_player = self.player
        max_depth = 200
        depth = 0

        while depth < max_depth:
            if current_state.is_terminal():
                winner = current_state.winner()
                if winner is not None:
                    return WIN_VALUE if winner == original_player else LOSS_VALUE
                return DRAW_VALUE

            actions = list(current_state.legal_moves())
            if not actions:
                return DRAW_VALUE

            action = self._biased_choice(actions, current_state)
            current_state = current_state.next_state(action)
            depth += 1

        return DRAW_VALUE

    # ------------------------------------------------------------------
    # Backpropagation — iterative to avoid recursion overhead
    # ------------------------------------------------------------------

    def backpropagate(self, result):
        node = self
        while node is not None:
            node.visits += 1
            if node.player is not None:
                node.wins += result
            # Flip perspective: WIN for child is LOSS for parent
            result = 1.0 - result
            node = node.parent

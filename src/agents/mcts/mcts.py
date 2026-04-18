import time
from .mcts_node import MCTSNode


def mcts_search(root_state, time_limit: float = 1.0) -> tuple:
    """
    Main MCTS algorithm — runs until the time budget expires.
    :param root_state: initial game state
    :param time_limit: seconds to spend searching
    :return: best action (x, y) coordinates
    """
    deadline = time.time() + time_limit
    root = MCTSNode(root_state, player=None)

    while time.time() < deadline:
        node = root

        # Selection: navigate to a leaf node
        while not node.is_terminal() and node.is_fully_expanded():
            node = node.best_child()

        # Expansion: add a new child if possible
        if not node.is_terminal():
            expanded_node = node.expand()
            if expanded_node is not None:
                node = expanded_node

        # Simulation: rollout from current node
        result = node.rollout()

        # Backpropagation: update statistics
        node.backpropagate(result)

    # Return the action of the most visited child
    if root.children:
        best_child = max(root.children, key=lambda child: child.visits)
        return best_child.action
    else:
        # Fallback: return a random legal move if no children were created
        legal_moves = list(root_state.legal_moves())
        return legal_moves[0] if legal_moves else None

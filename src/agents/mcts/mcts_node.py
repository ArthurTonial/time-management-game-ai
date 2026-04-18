import math
import random

WIN_VALUE = 1.0
LOSS_VALUE = 0.0
DRAW_VALUE = 0.5

class MCTSNode:
    """
    Node for Monte Carlo Tree Search
    """
    def __init__(self, state, parent=None, action=None, player=None):
        self.state = state
        self.parent = parent
        self.action = action  # The action that led to this state
        self.player = state.player
        self.children = [] # List of child nodes
        self.visits = 0
        self.wins = 0.0
        
        # Handle the case when state.player is None (terminal or no legal moves)
        if state.player is not None:
            self.untried_actions = list(state.legal_moves())
        else:
            self.untried_actions = []
    
    def is_terminal(self) -> bool:
        """Check if this node represents a terminal state"""
        return self.state.is_terminal()
        
    def is_fully_expanded(self) -> bool:
        """Check if all legal moves have been tried"""
        return len(self.untried_actions) == 0
    
    def expand(self):
        """Expand the tree by adding a new child node"""
        if not self.untried_actions:
            return None
        
        action = self.untried_actions.pop()
        next_state = self.state.next_state(action)
        child_node = MCTSNode(next_state, parent=self, action=action)
        self.children.append(child_node)
        return child_node
    
    def best_child(self, c: float = math.sqrt(2)):
        """Select the best child node using UCB1"""
        if not self.children:
            return None
            
        for child in self.children:
            if child.visits == 0:
                return child  # Prioritize unvisited nodes

        def ucb1(child):
            exploit = child.wins / child.visits
            explore = c * math.sqrt(math.log(self.visits) / child.visits)
            return exploit + explore

        return max(self.children, key=ucb1)
    
    def rollout(self):
        """Perform a rollout (simulation) from this node's state"""
        current_state = self.state.copy()
        original_player = self.player
        
        # Limit rollout depth to prevent infinite loops
        max_depth = 200
        depth = 0
        
        while depth < max_depth:
            # Check if game is over
            if current_state.is_terminal():
                winner = current_state.winner()
                if winner is not None:
                    # Return result from original player's perspective
                    if winner == original_player:
                        return WIN_VALUE
                    else:
                        return LOSS_VALUE
                else:
                    return DRAW_VALUE
            
            # Get legal moves
            actions = list(current_state.legal_moves())
            if not actions:
                return DRAW_VALUE
            
            # Make random move
            action = random.choice(actions)
            current_state = current_state.next_state(action)
            depth += 1
        
        # If we hit max depth, return draw
        return DRAW_VALUE

    def backpropagate(self, result):
        """Backpropagate the result up to the root"""
        self.visits += 1

        # Add the result to this node's wins
        if self.player is not None:
            self.wins += result

        # Flip the result for the parent (opponent's perspective)
        if self.parent is not None:
            # Invert the result: 1.0 becomes 0.0, 0.0 becomes 1.0, 0.5 stays 0.5
            if result == WIN_VALUE:
                parent_result = LOSS_VALUE
            elif result == LOSS_VALUE:
                parent_result = WIN_VALUE
            else:  # DRAW_VALUE
                parent_result = DRAW_VALUE
            
            self.parent.backpropagate(parent_result)

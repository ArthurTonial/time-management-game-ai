from typing import Tuple, Union
from .board import Board

class GameState:
    """
    The game state is simply the board 
    configuration and the player to move.
    All the "hard work" is done in the 
    board.Board class
    """

    game_name = "Gomoku"

    def __init__(self, board: Board, player: str) -> None:
        """
        Initializes the Game state with the given board and player to move.
        You can access the attributes self.board and self.player directly for convenience.

        :param board: the board configuration
        :param player: the player to move ('B' for Black, 'W' for White)
        """
        self.board = board
        self.player = player

    def is_terminal(self) -> bool:
        """
        Returns whether this state is terminal
        :return: bool
        """
        return self.board.is_terminal_state()

    def is_legal_move(self, move: Tuple[int, int]) -> bool:
        """
        Checks whether the given move (x, y) is legal in this state.
        :param move: tuple (x, y) representing column and row
        :return: bool
        """
        col, row = move
        return self.board.is_empty(row, col)

    def legal_moves(self) -> set:
        """
        Returns a set of legal moves in this state
        :return: set of tuples (x, y)
        """
        return self.board.legal_moves()

    def winner(self) -> Union[str, None]:
        """
        Returns the string representation of the winner of the game
        (if this is a terminal state)
        :return: 'B', 'W', or None
        """
        return self.board.winner()

    def get_board(self) -> Board:
        """
        Returns the board configuration
        :return: Board object
        """
        return self.board

    def copy(self) -> 'GameState':
        """
        Returns a copy of this state
        :return: GameState
        """
        return GameState(self.board.copy(), self.player)
    
    def next_state(self, move: Tuple[int, int]) -> 'GameState':
        """
        Returns the next state given the move.
        The next state is created as a new object
        (i.e. the move is not processed in-place)
        :param move: move in x,y (col,row) coordinates
        :return: GameState
        """
        if not self.is_legal_move(move):
            raise ValueError("Invalid move: %s" % str(move))
        
        new_state = self.copy()
        col, row = move
        new_state.board.place_marker(self.player, row, col)

        # Toggle the player for the next move
        new_state.player = Board.opponent(self.player)

        return new_state

def from_file(path_to_file: str) -> 'Board':
    """
    Generates a board from the string representation
    contained in the file
    :param path_to_file:
    :return: Board object
    """
    return Board.from_string(open(path_to_file).read())

class Board:
    """
    A board implementation for the Gomoku game
    """
    
    BLACK = 'B'
    WHITE = 'W'
    EMPTY = '.'
    
    def __init__(self, size=15):
        """
        Initialize the board with given size (default 15x15)
        """
        self.size = size
        self.board = [[self.EMPTY for _ in range(size)] for _ in range(size)]
        self.last_move = None

    def __str__(self):
        """
        Returns the string representation of the board
        :return: str
        """
        return '\n'.join([''.join(row) for row in self.board])

    @staticmethod
    def from_string(board_str: str) -> 'Board':
        """
        Generates a board from the string representation
        :param string:
        :return:
        """
        lines = board_str.strip().split('\n')
        if not lines:
            raise ValueError("Invalid board string representation. Empty input.")
        
        size = len(lines)
        if any(len(line) != size for line in lines):
            raise ValueError("Invalid board string representation. Missmatched line lengths.")

        board = Board(size)
        for row, line in enumerate(lines):
            for col, cell in enumerate(line):
                if cell in ['B', 'W', '.']:
                    board.board[row][col] = cell
                else:
                    raise ValueError("Invalid cell value in the board string representation")

        return board
    
    @staticmethod
    def opponent(color):
        """Returns the opponent of the received color"""
        if color == Board.EMPTY:
            raise ValueError('Empty has no opponent.')
        
        if color == Board.WHITE:
            return Board.BLACK
        else:
            return Board.WHITE


    
    def decorated_str(self, colors=False, move=None, highlight_flipped=False) -> str:
        """
        Returns the string representation of the board
        decorated with coordinates for board positions
        :param colors: whether to use colors (not implemented for Gomoku)
        :param move: tuple with position (row, col) to highlight the move done
        :param highlight_flipped: whether to highlight flipped pieces (not used in Gomoku)
        :return: str
        """
        result = '  '
        for col in range(min(self.size, 10)):
            result += str(col) + ' '
        if self.size > 10:
            for col in range(10, self.size):
                result += chr(ord('A') + col - 10) + ' '
        result += '\n'

        for row in range(self.size):
            if row < 10:
                result += str(row) + ' '
            else:
                result += chr(ord('A') + row - 10) + ' '
            
            for col in range(self.size):
                cell = self.board[row][col]
                if move and (row, col) == move:
                    result += '*' + cell + '*'
                else:
                    result += cell + ' '
            result += '\n'

        return result

    def place_marker(self, player, row, col):
        """
        Place a marker for the given player at the specified position
        :param player: Player color ('B' or 'W')
        :param row: Row position
        :param col: Column position
        """
        if not self.is_empty(row, col):
            raise ValueError("Invalid move")
        self.board[row][col] = player
        self.last_move = (row, col, player)

    def is_empty(self, row, col):
        """
        Check if the specified position is empty
        :param row: Row position
        :param col: Column position
        :return: bool
        """
        return (0 <= row < self.size and 
                0 <= col < self.size and 
                self.board[row][col] == self.EMPTY)

    def is_within_bounds(self, row, col):
        """
        Returns whether the move refers to a valid board position
        :param move: (int, int)
        :return: bool
        """
        return 0 <= row < self.size and 0 <= col < self.size

    def is_terminal_state(self):
        """Returns whether the current state is terminal (game finished) or not"""
        return (self._check_winner(self.BLACK) or 
                self._check_winner(self.WHITE) or 
                self._is_full())

    def winner(self):
        """Returns the color that has won the match, or None if no winner yet"""
        if self._check_winner(self.BLACK):
            return self.BLACK
        elif self._check_winner(self.WHITE):
            return self.WHITE
        else:
            return None

    def legal_moves(self) -> set:
        """Returns a set of legal moves (empty positions)"""
        moves = set()
        for row in range(self.size):
            for col in range(self.size):
                if self.is_empty(row, col):
                    moves.add((col, row))  # Return in (x, y) format like other games
        return moves

    def copy(self) -> 'Board':
        """
        Returns a copy of this board object
        :return: Board
        """
        new_board = Board(self.size)
        new_board.board = [row[:] for row in self.board]
        new_board.last_move = self.last_move
        return new_board
    
    def _is_full(self):
        """
        Check if the board is completely filled
        :return: bool
        """
        return all(cell != self.EMPTY for row in self.board for cell in row)

    def _check_winner(self, player, k=5):
        """
        Verify if the player has k in a row (default Gomoku = 5).
        :param player: Player color ('B' or 'W')
        :param k: Number of pieces in a row needed to win (default 5)
        :return: bool
        """
        directions = [(1,0), (0,1), (1,1), (1,-1)]  # vertical, horizontal, diagonals
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] != player:
                    continue
                for dr, dc in directions:
                    if all(
                        0 <= r + dr*i < self.size and
                        0 <= c + dc*i < self.size and
                        self.board[r + dr*i][c + dc*i] == player
                        for i in range(k)
                    ):
                        return True
        return False

import copy

class Board:
    """
    Connect 4 Game Board
    """

    P1symbol = "X"
    P2symbol = "O"
    WinLength = 4
    TerminalTurn = 2

    def __init__(self, width, height) -> None:
        self.width = width
        self.height = height
        self.board = [["+" for _ in range(width)] for _ in range(height)]
        self.column_heights = [0 for _ in range(width)]
        
        # 0 = P1, 1 = P2, 2 = Terminal
        self.turn = 0
        self.reward = 0

    def __str__(self) -> str:
        """
        Print the board
        """
        board = [" ".join([str(x) for x in row]) for row in reversed(self.board)]
        board.append("-" * (self.width*2-1))
        board.append(" ".join([str(x) for x in range(self.width)]))
        board.append("-" * (self.width*2-1))
        return "\n".join(board)
    
    def play(self, col) -> bool:
        """
        Play a piece in the column
        """
        height = self.column_heights[col]
        piece = Board.P1symbol if self.turn == 0 else Board.P2symbol

        # Out of bounds
        if col < 0 or col >= self.width:
            return False
    
        # Column is full
        if height >= self.height:
            return False
        
        # Game already over!
        if self.is_terminal():
            return False

        winner = self.check_win(col)

        # Game over! player won --> terminal
        if winner:
            points = 1 if self.turn == 0 else -1
            self.set_terminal(points)

        # Play turn!
        self.board[height][col] = piece
        self.column_heights[col] += 1
        self.update_turn()
        
        # Game over! board is full --> terminal
        if len(self.get_actions()) == 0:
            self.set_terminal(0)

        return True
    
    def set_terminal(self, reward) -> None:
        """
        Set the board to terminal
        """
        self.turn = Board.TerminalTurn
        self.reward = reward

    
    def get_turn(self) -> str:
        """
        Return the current turn
        """
        turn_map = {
            0 : Board.P1symbol,
            1 : Board.P2symbol,
            Board.TerminalTurn : "Terminal"
        }
        return turn_map[self.turn]
    
    def actor(self) -> int:
        """
        Return the current actor
        """
        return self.turn
    
    def get_actions(self) -> list:
        """
        Return a list of valid moves
        """
        return [col for col in range(self.width) if self.column_heights[col] < self.height]
    
    def successor(self, col):
        """
        Return a new board with the move played
        """
        new_board = copy.deepcopy(self)
        new_board.play(col)
        return new_board

    def is_terminal(self) -> bool:
        """
        Check if the game is over
        """
        return self.turn == 2 or len(self.get_actions()) == 0
    
    def update_turn(self) -> None:
        """
        Update the turn
        """
        if self.turn != Board.TerminalTurn:
            self.turn = (self.turn + 1) % 2

    def payoff(self) -> int:
        """
        Return the reward
        """
        return self.reward
    
    def check_win(self, col) -> bool:
        """
        Check if adding a piece to the column will win the game
        """
        
        direction_groups = [
            [(1,0), (-1,0)],    # Horizontal -
            [(0,1), (0,-1)],    # Vertical   |
            [(1,1), (-1,-1)],   # Diagonal   /
            [(1,-1), (-1,1)]    # Diagonal   \
        ]

        piece = Board.P1symbol if self.turn == 0 else Board.P2symbol
        row = self.column_heights[col]

        # Cannot win if the column is full
        if row >= self.height:
            return False

        for direction_group in direction_groups:
             
            # Count of number of continuous pieces in a line

            count = 1
            for dx, dy in direction_group:
                for i in range(1, 4):
                    x = col + i * dx
                    y = row + i * dy
                    if x < 0 or x >= self.width or y < 0 or y >= self.height:
                        break
                    if self.board[y][x] == piece:
                        count += 1
                    else:
                        break

            if count >= Board.WinLength:
                return True
            
        return False
    
    def check_opposing_win(self, col) -> bool:
        """
        Check if adding a piece to the column will cause the opponent to win
        """
        self.update_turn()
        result = self.check_win(col)
        self.update_turn()
        return result
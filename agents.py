import random
from abc import ABC, abstractmethod
from connect4 import Board
from mcts_node import mcts_policy

class InvalidMoveException(Exception):

    def __init__(self, move):
        self.move = move

class Agent(ABC):

    @abstractmethod
    def get_move(self, board: Board) -> int:
        pass

class HumanAgent(Agent):
    
    def get_move(self, board: Board) -> int:

        valid_moves = board.get_actions()

        while True:
            try:
                move = int(input("Enter a move: "))
                if move in valid_moves:
                    return move
                else:
                    raise InvalidMoveException(move)
            except InvalidMoveException:
                print("Invalid move! Must be within", valid_moves)
            except ValueError:
                print("Invalid move! Must be an integer.")

class RandomAgent(Agent):

    def get_move(self, board: Board) -> int:
        moves = board.get_actions()
        return random.choice(moves)
    
class RandomGreedyAgent(Agent):

    def get_move(self, board: Board) -> int:

        moves = board.get_actions()

        # Prioritize important moves
        for move in moves:
            # Win the game!
            if board.check_win(move):
                return move
            # Block the opponent from winning!
            if board.check_opposing_win(move):
                return move
        
        # Remove moves that lead to a loss the next turn!
        good_moves = []
        for move in moves:
            new_board = board.successor(move)
            opponent_win = new_board.check_win(move)
            if not opponent_win:
                good_moves.append(move)

        if good_moves:
            return random.choice(good_moves)
        else:
            return random.choice(moves)


class MonteCarloAgent(Agent):

    def __init__(self, duration, random_move_prob=0.05) -> None:
        super().__init__()
        self.random_move_prob = random_move_prob
        self.policy_fxn = mcts_policy(duration)

    def get_move(self, board: Board) -> int:

        # Occasional random move to introduce non-determinism
        if random.random() < self.random_move_prob:
            return random.choice(board.get_actions())
        else:
            return self.policy_fxn(board)
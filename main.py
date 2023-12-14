import argparse
import time
from connect4 import Board
from agents import Agent, HumanAgent, RandomAgent, RandomGreedyAgent, MonteCarloAgent

class Game:

    def __init__(self, p1_agent: Agent, p2_agent: Agent, width: int, height: int, turn_sleep: bool = False) -> None:

        self.width = width
        self.height = height
        self.p1_agent = p1_agent
        self.p2_agent = p2_agent
        self.turn_sleep = turn_sleep

    def play(self, extra_print=False) -> int:
        """
        Plays the game until a terminal state is reached:
            Returns 1 if P1 wins, -1 if P2 wins, 0 if tie
        """

        board = Board(self.width, self.height)

        while True:

            if self.turn_sleep:
                time.sleep(1)

            if extra_print:
                print(board)

            # Terminal Tie
            if len(board.get_actions()) == 0:
                if extra_print:
                    print("Tie!")
                return 0

            # Get move from agent
            current_turn = board.get_turn()
            agent = self.p1_agent if current_turn == Board.P1symbol else self.p2_agent
            move = agent.get_move(board)

            # Check if winning move & play!
            winner = board.check_win(move)
            valid = board.play(move)

            if winner:
                if extra_print:
                    print(board)
                    print("-"*10)
                    print(current_turn, "wins!")
                    print("-"*10)
                return 1 if current_turn == Board.P1symbol else -1
            
            if not valid:
                print("Warning: invalid move:", move)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Play Connect 4!")
    parser.add_argument("--play", nargs=2, choices=["human", "random", "greedy", "monte"], help="Choose two models to play.")
    parser.add_argument("--simulate", action='store_true', help="Let the models play against each other!")
    parser.add_argument("--turn_sleep", type=bool, default=False)
    parser.add_argument("--width", type=int, default=7)
    parser.add_argument("--height", type=int, default=6)
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--monte_carlo_time", type=float, default=2)

    args = parser.parse_args()

    width = args.width
    height = args.height
    count = args.count
    monte_carlo_time = args.monte_carlo_time
    turn_sleep = args.turn_sleep
    randomness = 0

    human = HumanAgent()
    random = RandomAgent()
    greedy = RandomGreedyAgent()
    monte = MonteCarloAgent(monte_carlo_time, randomness)

    string_to_agent = {
        "human": human,
        "random": random,
        "greedy": greedy,
        "monte": monte,
    }

    if args.play:
        p1_agent = string_to_agent[args.play[0]]
        p2_agent = string_to_agent[args.play[1]]
        game = Game(p1_agent, p2_agent, width, height, turn_sleep)
        game.play(extra_print=True)

    # Simulate all possible games!
    if args.simulate:

        def simulate_matchups(p1: Agent, p2: Agent, width: int, height: int, count: int) -> tuple:
            game = Game(p1, p2, width, height)
            p1_wins, p2_wins, ties = 0, 0, 0
            for _ in range(count):
                result = game.play()
                if result == 1:
                    p1_wins += 1
                elif result == -1:
                    p2_wins += 1
                else:
                    ties += 1
            return p1_wins, p2_wins, ties
        
        setups = [
            ((random, random), ("Random", "Random")),
            ((random, greedy), ("Random", "Greedy")),
            ((greedy, greedy), ("Greedy", "Greedy")),
            ((random, monte), ("Random", "Monte Carlo")),
            ((greedy, monte), ("Greedy", "Monte Carlo")),
            ((monte, monte), ("Monte Carlo", "Monte Carlo")),
        ]

        for config, names in setups:
            p1_wins, p2_wins, ties = simulate_matchups(*config, width, height, count)
            print(f"{names[0]}: {round(p1_wins/count*100, 3)}%",
                f"{names[1]}: {round(p2_wins/count*100, 3)}%",
                f"Ties: {round(ties/count*100, 3)}%",
                sep="\t"
                )

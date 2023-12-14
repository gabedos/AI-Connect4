import random
import time
from connect4 import Board
import math

class MonteCarloNode:

    def __init__(self, state : Board, parent=None, parent_action=None):

        self.state = state
        self.parent = parent
        self.parent_action = parent_action

        self.total_visits = 0
        self.total_rewards = 0

        self.children = []

        if self.state.is_terminal():
            self.missing_child_actions = []
        else:
            self.missing_child_actions = self.state.get_actions()

    def is_fully_expanded(self):
        """
        Determines if the node is fully expanded.
        """
        return len(self.missing_child_actions) == 0

    def get_average_reward(self):
        if self.total_visits == 0:
            return 0
        return self.total_rewards / self.total_visits

    def get_best_average_child(self):
        """
        Returns the child node with the best average reward.
        """

        if self.state.actor() == 0:
            node = max(self.children, key = lambda x: x.get_average_reward())
        else:
            node = min(self.children, key = lambda x: x.get_average_reward())
        return node

    def get_ucb_value(self, parent_total_visits, parent_actor):
        """
        Returns the UCB value of the node using parents visits and actor
        """

        if parent_actor == 0:
            value = self.get_average_reward() + math.sqrt(2 * math.log(parent_total_visits) / self.total_visits)
        else:
            value = self.get_average_reward() - math.sqrt(2 * math.log(parent_total_visits) / self.total_visits)
        return value

    def get_best_ucb_child(self):
        """
        Returns the child node with the best UCB value.
        """

        if self.state.actor() == 0:
            node = max(self.children, key = lambda x: x.get_ucb_value(self.total_visits, self.state.actor()))
        else:
            node = min(self.children, key = lambda x: x.get_ucb_value(self.total_visits, self.state.actor()))
        return node
    
    def expand(self):
        """
        Expands the node by adding a new child node from an unexplored action.
        """
        action = self.missing_child_actions.pop()
        next_state = self.state.successor(action)
        child_node = MonteCarloNode(next_state, parent=self, parent_action=action)
        self.children.append(child_node)
        return child_node

    def find_leaf_node(self):
        """
        Returns the leaf node of the tree using UCB values.
        """

        current_node = self
        while not current_node.state.is_terminal():
            
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.get_best_ucb_child()
        return current_node
    
    def simulate(self):
        """
        Returns the terminal value of the node by randomly simulating game.
        """

        state = self.state
        while not state.is_terminal():
            state = state.successor(random.choice(state.get_actions()))
        return state.payoff()
    
    def update_rewards(self, reward):
        """
        Updates the total reward and total visits of the node and all its parents.
        """

        parent_node = self
        while parent_node is not None:
            parent_node.total_rewards += reward
            parent_node.total_visits += 1
            parent_node = parent_node.parent

    def __str__(self) -> str:

        ucb_value = "N/A"
        if self.parent:
            ucb_value = self.get_ucb_value(self.parent.total_visits, self.parent.state.actor())

        string_form = f"""
        Node: {self.state}
        Total Visits: {self.total_visits}
        Total Rewards: {self.total_rewards}
        Average Reward: {self.get_average_reward()}
        UCB Value: {ucb_value}
        Parent Action: {self.parent_action}
        Actor: {self.state.actor()}
        Missing Child Actions: {self.missing_child_actions}
        Children: {len(self.children)}
        """

        return string_form


def mcts_policy(time_duration):

    def fxn(initial_position: Board):

        start_time = time.time()

        root = MonteCarloNode(initial_position, None)

        # Learning while time remains
        while time.time() - start_time < time_duration:

            # Gets the leaf node in the UCB tree
            node = root.find_leaf_node()

            # Determines the random terminal value of the node
            reward = node.simulate()

            # Updates the rewards of the parents
            node.update_rewards(reward)

        node = root.get_best_average_child()

        # print(root, node)

        return node.parent_action

    return fxn

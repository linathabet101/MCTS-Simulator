import random

class Node:
    def __init__(self, state):
        self.state = state
        self.children = []
        self.reward = 0
        self.visits = 0

class MCTS:
    def __init__(self, root_node, simulations=100):
        self.root = root_node
        self.simulations = simulations

    def best_action(self):
        """Perform the MCTS algorithm to choose the best action."""
        for _ in range(self.simulations):
            self.tree_policy(self.root)

        return self.best_child(self.root)

    def tree_policy(self, node):
        """Expand the node by performing the MCTS tree policy."""
        while not self.is_terminal(node):
            if len(node.children) < 4:  # Max actions
                node.children.append(Node(random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])))
            else:
                node = self.best_child(node)

    def best_child(self, node):
        """Select the best child node based on the maximum reward."""
        return max(node.children, key=lambda x: x.reward)

    def is_terminal(self, node):
        """Check if the node is terminal (goal reached or obstacle hit)."""
        return node.state == 'G' or node.state == 'X'

import math
import random
import torch
import numpy as np
from neural_network import PolicyValueNetwork

class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0
        self.action = action  # Store the action that led to this node

    def expand(self, environment):
        """Expand node by creating child nodes for all possible actions."""
        possible_actions = environment.get_possible_actions()
        for action in possible_actions:
            # Create a copy of the environment to avoid modifying the original
            env_copy = type(environment)()
            env_copy.state = environment.state
            # Apply the action to get the new state
            new_state = env_copy.apply_action(action)
            # Create a child node with the new state and action
            child = Node(new_state, parent=self, action=action)
            self.children.append(child)

    def best_child(self, exploration_weight=1.4):
        """Select the child with the highest UCB score."""
        if not self.children:
            return None
        
        return max(
            self.children,
            key=lambda c: (c.value / (c.visits + 1e-6)) + exploration_weight * math.sqrt(math.log(self.visits + 1) / (c.visits + 1e-6))
        )


class MCTS:
    def __init__(self, environment, iterations=1000, exploration_weight=1.4):
        self.environment = environment
        self.iterations = iterations
        self.exploration_weight = exploration_weight

    def search(self, root_state):
        root = Node(root_state)
        for _ in range(self.iterations):
            node = self.select(root)
            node.expand(self.environment)
            reward = self.simulate(node)
            self.backpropagate(node, reward)
        return root

    def select(self, node):
        """Select a leaf node by traversing the tree using UCB policy."""
        while node.children:
            best_child = node.best_child(self.exploration_weight)
            if best_child is None:
                break
            node = best_child
        return node

    def simulate(self, node):
        """Simulate a random playout from the given node."""
        return random.uniform(0, 1)

    def backpropagate(self, node, reward):
        """Update node statistics going up the tree."""
        while node:
            node.visits += 1
            node.value += reward
            node = node.parent


class NestedMCTS(MCTS):
    def __init__(self, environment, iterations=1000, nesting_level=2, exploration_weight=1.4):
        super().__init__(environment, iterations, exploration_weight)
        self.nesting_level = nesting_level

    def simulate(self, node, level=None):
        """Simulate using nested Monte Carlo search."""
        if level is None:
            level = self.nesting_level
        if level == 0:
            return random.uniform(0, 1)
        else:
            best_reward = -float('inf')
            for _ in range(10):  # Number of nested simulations
                reward = self.simulate(node, level - 1)
                if reward > best_reward:
                    best_reward = reward
            return best_reward


class NRPA(MCTS):
    def __init__(self, environment, iterations=1000, exploration_weight=1.4):
        super().__init__(environment, iterations, exploration_weight)
        self.policy = {}

    def simulate(self, node):
        """Simulate using a learned policy."""
        # Convert state to a hashable form
        state_hash = self._hash_state(node.state)
        
        # Initialize policy for this state if needed
        possible_actions = self.environment.get_possible_actions()
        if state_hash not in self.policy:
            self.policy[state_hash] = np.ones(len(possible_actions))
        
        # Use policy to select action
        action_probs = self.policy[state_hash] / np.sum(self.policy[state_hash])
        if len(possible_actions) > 0 and len(action_probs) > 0:
            try:
                action_idx = np.random.choice(len(possible_actions), p=action_probs)
                action = possible_actions[action_idx]
                
                # Apply action to get new state
                env_copy = type(self.environment)()
                env_copy.state = node.state
                env_copy.apply_action(action)
            except (ValueError, IndexError):
                pass  # Fall back to random reward if there's an issue
        
        return random.uniform(0, 1)
    
    def _hash_state(self, state):
        """Convert state to a hashable form."""
        if isinstance(state, (list, np.ndarray)):
            # For list-like objects
            if isinstance(state[0], (list, np.ndarray)):
                # If it's a 2D structure like a board
                return tuple(tuple(row) if isinstance(row, (list, np.ndarray)) else row for row in state)
            else:
                # If it's a 1D list
                return tuple(state)
        elif isinstance(state, tuple):
            # If it's already a tuple, check if elements need conversion
            if state and isinstance(state[0], (list, np.ndarray)):
                board, player = state
                board_tuple = tuple(tuple(row) for row in board)
                return (board_tuple, player)
            return state
        else:
            # For primitive types or custom objects
            return state


class AlphaZeroMCTS(MCTS):
    def __init__(self, environment, iterations=1000, exploration_weight=1.4):
        super().__init__(environment, iterations, exploration_weight)
        # Get the number of possible actions
        possible_actions = environment.get_possible_actions()
        action_size = len(possible_actions)
        
        # Ensure input_size is valid (at least 1)
        input_size = 10  # Default input size
        self.network = PolicyValueNetwork(input_size=input_size, hidden_size=64, output_size=action_size)

    def select(self, node):
        """Select a node using the policy network."""
        current = node
        while current.children:
            try:
                # Process state for the neural network
                state_tensor = self._prepare_state_tensor(current.state)
                
                # Get policy prediction from the network
                policy, _ = self.network(state_tensor)
                policy = policy.squeeze().detach().numpy()
                
                # Select child with highest policy value
                if len(policy) > 0 and current.children:
                    # Simple selection of child with highest policy score
                    best_child = current.children[0]
                    best_score = float('-inf')
                    
                    for i, child in enumerate(current.children):
                        # Ensure index is in bounds
                        idx = min(i, len(policy) - 1)
                        score = policy[idx]
                        if score > best_score:
                            best_score = score
                            best_child = child
                    
                    current = best_child
                else:
                    break
            except Exception as e:
                # Fallback to UCB selection in case of error
                best_child = current.best_child(self.exploration_weight)
                if best_child is None:
                    break
                current = best_child
        
        return current

    def simulate(self, node):
        """Simulate using the value network."""
        try:
            # Process state for the neural network
            state_tensor = self._prepare_state_tensor(node.state)
            
            # Get value prediction from the network
            _, value = self.network(state_tensor)
            return value.item()
        except:
            # Fall back to random simulation if there's an error
            return random.uniform(0, 1)

    def _prepare_state_tensor(self, state):
        """Prepare state as input tensor for the neural network."""
        # Convert state to a flat array
        state_array = self._flatten_state(state)
        
        # Ensure it has the right shape (10 features)
        if len(state_array) < 10:
            state_array = np.pad(state_array, (0, 10 - len(state_array)), mode='constant')
        elif len(state_array) > 10:
            state_array = state_array[:10]
        
        # Convert to tensor and add batch dimension
        return torch.FloatTensor(state_array).unsqueeze(0)

    def _flatten_state(self, state):
        """Convert any state representation to a flat array."""
        if isinstance(state, int):
            return np.array([float(state)])
        elif isinstance(state, (list, np.ndarray)):
            if isinstance(state[0], (list, np.ndarray)):
                # 2D array (like a board)
                return np.array([float(x) for row in state for x in row])
            else:
                # 1D array
                return np.array([float(x) for x in state])
        elif isinstance(state, tuple):
            # If state is a tuple (e.g., (board, player))
            if len(state) == 2 and isinstance(state[0], (list, np.ndarray)):
                board, player = state
                flattened = [float(x) for row in board for x in row]
                flattened.append(float(player))
                return np.array(flattened)
            else:
                # Regular tuple
                return np.array([float(x) for x in state])
        else:
            # Fallback for other types
            return np.array([1.0])  # Ensure at least one element
# MCTS Simulator

This project is a Monte Carlo Tree Search (MCTS) simulator with a graphical user interface (GUI). It allows users to explore different MCTS variants, environments, and optimizations. The simulator is designed to help users understand how MCTS works and visualize the search tree in real-time.

## Features

### Environments:
- **Simple**: A basic environment with left/right/stay actions.
- **Breakthrough**: A 5x5 board game where players try to reach the opponent's side.
- **Connect Four**: A 6x7 board game where players aim to connect four pieces.
- **Tic-Tac-Toe**: A 3x3 board game where players aim to get three in a row.

### MCTS Variants:
- **Basic MCTS**: Standard Monte Carlo Tree Search.
- **Nested MCTS**: Nested Monte Carlo Tree Search with configurable depth.
- **NRPA**: Nested Rollout Policy Adaptation.
- **AlphaZero MCTS**: MCTS with a neural network for policy and value estimation.

### Optimizations:
- **Parallel MCTS**
- **Tree Pruning**
- **Progressive Widening**
- **Heuristic Evaluation**
- **Virtual Loss**
- **RAVE (Rapid Action Value Estimation)**
- **Transposition Table**
- **ML Policy Guidance**

### Visualization:
- Real-time tree visualization with zoom and pan support.
- Color-coded nodes for root, best path, expanded nodes, leaf nodes, and default nodes.

## Installation

### Prerequisites:
- Python 3.8 or higher.
- Required Python packages: tkinter, numpy, torch.

## User Guide

### 1. Launch the Interface
Run `main.py` to launch the MCTS Simulator interface.

### 2. Configure Simulation Settings
- **Environment**: Select the environment (e.g., Simple, Breakthrough, Connect Four, Tic-Tac-Toe).
- **MCTS Variant**: Choose the MCTS algorithm (e.g., Basic MCTS, AlphaZero MCTS).
- **Iterations**: Set the number of iterations for the simulation (e.g., 1000).
- **Exploration (C)**: Set the exploration constant for the UCB formula (e.g., 1.4).
- **Sim Depth**: Set the simulation depth (e.g., 10).

### 3. Enable Use Cases & Optimizations
Use the checkboxes to enable advanced features like Parallel MCTS, Tree Pruning, or ML Policy Guidance.

### 4. Run the Simulation
Click the ▶ Run button to start the simulation.
- The progress bar will show the simulation progress.
- The Tree Visualization section will display the MCTS tree in real-time.
- The Simulation Output section will log the steps of the simulation.

### 5. Pause or Stop the Simulation
- Use the ⏸ Pause button to pause the simulation.
- Use the ▶ Resume button to resume the simulation.
- Use the ⏹ Stop button to stop the simulation early.

### 6. Adjust Visualization
- Use the ➕ Zoom In and ➖ Zoom Out buttons to adjust the tree visualization.
- Use the 🔄 Reset View button to reset the zoom level.

### 7. Review Simulation Output
The Simulation Output section logs the following:
- Selection, expansion, simulation, and backpropagation steps.
- Final results of the simulation.

## Understanding the Tree Visualization

### Node Colors:
- **Green**: Root node (starting point of the tree).
- **Orange**: Nodes on the best path (most promising actions).
- **Blue**: Expanded nodes (nodes with children).
- **Purple**: Leaf nodes (nodes without children).
- **Grey**: Default nodes (other nodes in the tree).

### Node Values:
Each node displays two values:
- **V**: The cumulative reward from simulations passing through this node.
- **N**: The number of times the node has been visited.

### What V and N Mean:
- **V (Value)**: Represents the total reward obtained from simulations that passed through this node. A higher V means the node leads to better outcomes.
- **N (Visits)**: Represents the number of times the node has been visited during the simulation. A higher N means the node has been explored more frequently.

### How to Interpret V and N:
- **High N, High V**: The node is frequently visited and leads to good outcomes. It is likely part of the best path.
- **High N, Low V**: The node is frequently visited but leads to poor outcomes. The algorithm may be exploring this path to confirm its quality.
- **Low N, High V**: The node has not been explored much but shows promising results. The algorithm may explore it more in future iterations.
- **Low N, Low V**: The node has not been explored much and does not show promising results. It is likely a less important part of the tree.

### Example Configuration:
- **Environment**: Tic-Tac-Toe
- **MCTS Variant**: AlphaZero MCTS
- **Iterations**: 1000
- **Exploration (C)**: 1.4
- **Sim Depth**: 10

### Use Cases:
- Enable **ML Policy Guidance**.
- Enable **Tree Pruning**.

## Student:
- Rodrigue Migniha
- Lina Thabet

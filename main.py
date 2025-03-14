import tkinter as tk
from environment import Environment
from mcts import MCTS, Node
import time


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("MCTS Agent")

        # Initialize environment, agent, and MCTS
        self.env = Environment()
        self.node = Node(self.env.reset())
        self.mcts = MCTS(self.node, simulations=500)

        # Setup UI components
        self.setup_ui()

    def setup_ui(self):
        """Set up the Tkinter UI elements."""
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(pady=20)

        self.info_label = tk.Label(self.info_frame, text="Agent's Actions", font=("Helvetica", 16))
        self.info_label.grid(row=0, column=0, columnspan=2)

        self.action_label = tk.Label(self.info_frame, text="Current Action: ", font=("Helvetica", 14))
        self.action_label.grid(row=1, column=0, sticky="w")

        self.reward_label = tk.Label(self.info_frame, text="Reward: 0", font=("Helvetica", 14))
        self.reward_label.grid(row=1, column=1, sticky="e")

        self.canvas = tk.Canvas(self.root, width=400, height=400, bg="white")
        self.canvas.pack(pady=20)

        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=10)

        self.step_button = tk.Button(self.control_frame, text="Take Step", font=("Helvetica", 14), command=self.take_step)
        self.step_button.grid(row=0, column=0, padx=10)

        self.reset_button = tk.Button(self.control_frame, text="Reset Environment", font=("Helvetica", 14), command=self.reset_env)
        self.reset_button.grid(row=0, column=1, padx=10)

        self.progress_label = tk.Label(self.root, text="Progress: 0%", font=("Helvetica", 12))
        self.progress_label.pack(pady=10)

        self.status_label = tk.Label(self.root, text="Status: Waiting for action...", font=("Helvetica", 12))
        self.status_label.pack(pady=5)

        self.update_ui()

    def update_ui(self):
        """Updates the environment grid and feedback text."""
        self.canvas.delete("all")
        grid = self.env.render().split('\n')
        for y, row in enumerate(grid):
            for x, cell in enumerate(row.split()):
                color = 'white' if cell == ' ' else 'red' if cell == 'X' else 'green' if cell == 'G' else 'blue'
                self.canvas.create_rectangle(x * 80, y * 80, (x + 1) * 80, (y + 1) * 80, fill=color)

        self.reward_label.config(text=f"Reward: {self.get_reward()}")
        self.action_label.config(text=f"Current Action: {self.get_action()}")

        self.root.after(100, self.update_ui)

    def get_action(self):
        """Return the current action based on MCTS."""
        return self.mcts.best_action().state

    def get_reward(self):
        """Return the current reward of the agent."""
        state, reward = self.env.step(self.get_action())
        return reward

    def take_step(self):
        """Handle one step of the agent's decision-making."""
        self.status_label.config(text="Status: Making decision...")

        action = self.mcts.best_action()
        state, reward = self.env.step(action)

        self.status_label.config(text="Status: Step taken successfully!")

    def reset_env(self):
        """Reset the environment to the initial state."""
        self.env.reset()
        self.update_ui()
        self.status_label.config(text="Status: Environment reset.")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

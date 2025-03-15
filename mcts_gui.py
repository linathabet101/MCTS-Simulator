import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import time
import threading
import queue
from mcts import MCTS, NestedMCTS, NRPA, AlphaZeroMCTS, Node
from environment import SimpleEnvironment, BreakthroughEnvironment, ConnectFourEnvironment, TicTacToeEnvironment
from visualization import Visualization

class MCTSApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Monte Carlo Tree Search (MCTS) Simulator")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f0f0f0")
        
        # Set up a modern style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", background="#4CAF50", foreground="white", font=("Arial", 10))
        style.configure("TCheckbutton", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("TFrame", background="#f0f0f0")
        
        # Main frames
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.settings_frame = ttk.LabelFrame(self.root, text="Simulation Settings")
        self.settings_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.usecase_frame = ttk.LabelFrame(self.root, text="Use Cases & Optimizations")
        self.usecase_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.visualization_frame = ttk.LabelFrame(self.root, text="Tree Visualization")
        self.visualization_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.output_frame = ttk.LabelFrame(self.root, text="Simulation Output")
        self.output_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Welcome message
        self.welcome_label = tk.Label(
            self.top_frame,
            text="Monte Carlo Tree Search (MCTS) Simulator",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
            fg="#333333",
        )
        self.welcome_label.pack(pady=10)

        # Settings grid layout
        self.create_settings_widgets()
        
        # Use cases grid layout
        self.create_usecase_widgets()
        
        # Create visualization canvas
        self.create_visualization_canvas()
        
        # Create output text area
        self.create_output_widgets()
        
        # Initialize visualization
        self.visualization = Visualization(self.canvas)
        
        # Simulation state variables
        self.paused = False
        self.running = False
        self.simulation_thread = None
        self.message_queue = queue.Queue()
        self.root.after(100, self.check_queue)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.output_frame, orient="horizontal", length=1000, mode="determinate")
        self.progress.pack(pady=10, fill=tk.X, padx=10)
        
        # Add zoom controls for visualization
        self.create_zoom_controls()

    def create_settings_widgets(self):
        # Create a grid layout for settings
        settings_grid = ttk.Frame(self.settings_frame)
        settings_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Row 0: Environment selection
        ttk.Label(settings_grid, text="Environment:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.env_var = tk.StringVar(value="Simple")
        self.env_menu = ttk.Combobox(
            settings_grid,
            textvariable=self.env_var,
            values=["Simple", "Breakthrough", "Connect Four", "Tic-Tac-Toe"],
            width=15,
            state="readonly",
        )
        self.env_menu.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # MCTS variant selection
        ttk.Label(settings_grid, text="MCTS Variant:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.mcts_var = tk.StringVar(value="Basic MCTS")
        self.mcts_menu = ttk.Combobox(
            settings_grid,
            textvariable=self.mcts_var,
            values=["Basic MCTS", "Nested MCTS", "NRPA", "AlphaZero MCTS"],
            width=15,
            state="readonly",
        )
        self.mcts_menu.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Iterations input
        ttk.Label(settings_grid, text="Iterations:").grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        self.iter_var = tk.StringVar(value="1000")
        self.iter_entry = ttk.Entry(settings_grid, textvariable=self.iter_var, width=10)
        self.iter_entry.grid(row=0, column=5, sticky=tk.W, padx=5, pady=5)
        
        # Exploration constant
        ttk.Label(settings_grid, text="Exploration (C):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.exploration_var = tk.StringVar(value="1.4")
        self.exploration_entry = ttk.Entry(settings_grid, textvariable=self.exploration_var, width=10)
        self.exploration_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Simulation depth
        ttk.Label(settings_grid, text="Sim Depth:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.depth_var = tk.StringVar(value="10")
        self.depth_entry = ttk.Entry(settings_grid, textvariable=self.depth_var, width=10)
        self.depth_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Control buttons
        self.control_frame = ttk.Frame(settings_grid)
        self.control_frame.grid(row=1, column=4, columnspan=2, sticky=tk.E, padx=5, pady=5)
        
        self.run_button = ttk.Button(
            self.control_frame,
            text="▶ Run",
            command=self.start_simulation,
            style="TButton"
        )
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = ttk.Button(
            self.control_frame,
            text="⏸ Pause",
            command=self.toggle_pause,
            state=tk.DISABLED
        )
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            self.control_frame,
            text="⏹ Stop",
            command=self.stop_simulation,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

    def create_usecase_widgets(self):
        # Set up use cases with checkboxes in a grid
        usecase_grid = ttk.Frame(self.usecase_frame)
        usecase_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Define use cases
        self.use_cases = {
            "parallel": {"var": tk.BooleanVar(value=False), "text": "Parallel MCTS", 
                        "tooltip": "Run simulations in parallel threads"},
            "pruning": {"var": tk.BooleanVar(value=False), "text": "Tree Pruning", 
                      "tooltip": "Prune branches with low visit counts"},
            "progressive": {"var": tk.BooleanVar(value=False), "text": "Progressive Widening", 
                          "tooltip": "Gradually add actions to the tree"},
            "heuristic": {"var": tk.BooleanVar(value=False), "text": "Heuristic Evaluation", 
                        "tooltip": "Use domain knowledge to guide simulations"},
            "virtual_loss": {"var": tk.BooleanVar(value=False), "text": "Virtual Loss", 
                           "tooltip": "Discourage thread collisions in parallel search"},
            "rave": {"var": tk.BooleanVar(value=False), "text": "RAVE", 
                   "tooltip": "Rapid Action Value Estimation for faster learning"},
            "transposition": {"var": tk.BooleanVar(value=False), "text": "Transposition Table", 
                            "tooltip": "Cache and reuse subtrees for equivalent states"},
            "ml_policy": {"var": tk.BooleanVar(value=False), "text": "ML Policy Guidance", 
                        "tooltip": "Use trained policy network to guide search"},
        }
        
        # Create checkboxes in a 2x4 grid
        row, col = 0, 0
        for key, case in self.use_cases.items():
            cb = ttk.Checkbutton(usecase_grid, text=case["text"], variable=case["var"])
            cb.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
            
            # Create tooltip
            self.create_tooltip(cb, case["tooltip"])
            
            # Update position for next checkbox
            col += 1
            if col > 3:  # 4 columns
                col = 0
                row += 1
                
        # Add use case presets dropdown
        preset_frame = ttk.Frame(usecase_grid)
        preset_frame.grid(row=row+1, column=0, columnspan=4, sticky=tk.W, padx=5, pady=10)
        
        ttk.Label(preset_frame, text="Optimization Presets:").pack(side=tk.LEFT, padx=5)
        
        self.preset_var = tk.StringVar(value="None")
        presets = ["None", "Performance", "Memory Efficient", "ML Enhanced", "Deterministic"]
        self.preset_menu = ttk.Combobox(
            preset_frame,
            textvariable=self.preset_var,
            values=presets,
            width=15,
            state="readonly"
        )
        self.preset_menu.pack(side=tk.LEFT, padx=5)
        self.preset_menu.bind("<<ComboboxSelected>>", self.apply_preset)

    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            # Create a toplevel window
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = ttk.Label(
                self.tooltip, text=text, background="#ffffe0", 
                relief="solid", borderwidth=1, padding=(5, 3)
            )
            label.pack()
            
        def leave(event):
            if hasattr(self, "tooltip"):
                self.tooltip.destroy()
                
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def create_visualization_canvas(self):
        # Create canvas with scrollbars
        canvas_frame = ttk.Frame(self.visualization_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white")
        
        # Add scrollbars
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        # Configure canvas scroll region
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Grid layout for canvas and scrollbars
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        # Add ability to zoom with mousewheel
        self.canvas.bind("<MouseWheel>", self.zoom_canvas)  # Windows
        self.canvas.bind("<Button-4>", self.zoom_canvas)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.zoom_canvas)    # Linux scroll down

    def create_zoom_controls(self):
        """Create zoom controls for the visualization"""
        zoom_frame = ttk.Frame(self.visualization_frame)
        zoom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(zoom_frame, text="➕ Zoom In", command=lambda: self.zoom_canvas(None, zoom_in=True)).pack(side=tk.LEFT, padx=5)
        ttk.Button(zoom_frame, text="➖ Zoom Out", command=lambda: self.zoom_canvas(None, zoom_in=False)).pack(side=tk.LEFT, padx=5)
        ttk.Button(zoom_frame, text="🔄 Reset View", command=self.reset_zoom).pack(side=tk.LEFT, padx=5)
        
        # Color legend
        legend_frame = ttk.Frame(zoom_frame)
        legend_frame.pack(side=tk.RIGHT, padx=10)
        
        ttk.Label(legend_frame, text="Legend:").pack(side=tk.LEFT)
        
        # Create color samples with labels
        colors = [
            ("#4CAF50", "Root"), 
            ("#FF5722", "Best Path"),
            ("#2196F3", "Expanded"),
            ("#9C27B0", "Leaf"),
            ("#607D8B", "Other")
        ]
        
        for color, label in colors:
            sample_frame = ttk.Frame(legend_frame)
            sample_frame.pack(side=tk.LEFT, padx=5)
            
            color_sample = tk.Canvas(sample_frame, width=15, height=15, bg=color, highlightthickness=1)
            color_sample.pack(side=tk.LEFT, padx=2)
            
            ttk.Label(sample_frame, text=label, font=("Arial", 8)).pack(side=tk.LEFT)

    def create_output_widgets(self):
        """Create output text area with scrollbars"""
        # Create text widget with scrollbar
        self.output_text = scrolledtext.ScrolledText(
            self.output_frame,
            wrap=tk.WORD,
            width=100,
            height=15,  # Increased height for better visibility
            font=("Arial", 10)
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def zoom_canvas(self, event=None, zoom_in=True):
        """Zoom in or out of the canvas"""
        zoom_factor = 1.1 if zoom_in else 0.9
        self.visualization.zoom *= zoom_factor
        self.canvas.scale("all", 0, 0, zoom_factor, zoom_factor)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def reset_zoom(self):
        """Reset the canvas zoom to default"""
        self.visualization.zoom = 1.0
        self.canvas.scale("all", 0, 0, 1 / self.visualization.zoom, 1 / self.visualization.zoom)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def apply_preset(self, event=None):
        """Apply a preset configuration for use cases"""
        preset = self.preset_var.get()
        if preset == "Performance":
            self.use_cases["parallel"]["var"].set(True)
            self.use_cases["virtual_loss"]["var"].set(True)
            self.use_cases["rave"]["var"].set(True)
        elif preset == "Memory Efficient":
            self.use_cases["pruning"]["var"].set(True)
            self.use_cases["transposition"]["var"].set(True)
        elif preset == "ML Enhanced":
            self.use_cases["ml_policy"]["var"].set(True)
            self.use_cases["heuristic"]["var"].set(True)
        elif preset == "Deterministic":
            self.use_cases["progressive"]["var"].set(True)
            self.use_cases["heuristic"]["var"].set(True)
        else:
            for case in self.use_cases.values():
                case["var"].set(False)

    def start_simulation(self):
        """Start the MCTS simulation in a separate thread"""
        if self.running:
            return

        # Get user inputs
        env_name = self.env_var.get()
        mcts_variant = self.mcts_var.get()
        try:
            iterations = int(self.iter_var.get())
            exploration = float(self.exploration_var.get())
            sim_depth = int(self.depth_var.get())
            if iterations <= 0 or exploration < 0 or sim_depth <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter valid simulation parameters.")
            return

        # Initialize environment
        if env_name == "Simple":
            environment = SimpleEnvironment()
        elif env_name == "Breakthrough":
            environment = BreakthroughEnvironment()
        elif env_name == "Connect Four":
            environment = ConnectFourEnvironment()
        elif env_name == "Tic-Tac-Toe":
            environment = TicTacToeEnvironment()
        else:
            messagebox.showerror("Error", f"Invalid environment selected: {env_name}")
            return

        # Initialize MCTS variant
        if mcts_variant == "Basic MCTS":
            mcts = MCTS(environment, iterations, exploration_weight=exploration)
        elif mcts_variant == "Nested MCTS":
            mcts = NestedMCTS(environment, iterations, nesting_level=sim_depth, exploration_weight=exploration)
        elif mcts_variant == "NRPA":
            mcts = NRPA(environment, iterations, exploration_weight=exploration)
        elif mcts_variant == "AlphaZero MCTS":
            mcts = AlphaZeroMCTS(environment, iterations, exploration_weight=exploration)
        else:
            messagebox.showerror("Error", "Invalid MCTS variant selected.")
            return

        # Enable/disable controls
        self.run_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)

        # Start simulation in a separate thread
        self.running = True
        self.simulation_thread = threading.Thread(
            target=self.run_simulation,
            args=(mcts, environment, iterations)
        )
        self.simulation_thread.start()

    def run_simulation(self, mcts, environment, iterations):
        """Run the MCTS simulation"""
        root = Node(environment.state)
        for i in range(iterations):
            if not self.running:
                break

            while self.paused:
                time.sleep(0.1)

            # Step 1: Selection
            node = mcts.select(root)
            self.message_queue.put(("update_explanation", "Step 1: Selection - Traversing the tree to select a node"))
            self.message_queue.put(("update_tree", root))

            # Step 2: Expansion
            node.expand(environment)
            self.message_queue.put(("update_explanation", "Step 2: Expansion - Expanding the selected node"))
            self.message_queue.put(("update_tree", root))

            # Step 3: Simulation
            reward = mcts.simulate(node)
            self.message_queue.put(("update_explanation", "Step 3: Simulation - Simulating a random playout"))
            self.message_queue.put(("update_tree", root))

            # Step 4: Backpropagation
            mcts.backpropagate(node, reward)
            self.message_queue.put(("update_explanation", "Step 4: Backpropagation - Updating node statistics"))
            self.message_queue.put(("update_tree", root))

            # Update progress bar
            self.message_queue.put(("update_progress", i + 1))

        # Simulation finished
        self.message_queue.put(("simulation_finished", None))

    def toggle_pause(self):
        """Toggle pause/resume for the simulation"""
        self.paused = not self.paused
        if self.paused:
            self.pause_button.config(text="▶ Resume")
        else:
            self.pause_button.config(text="⏸ Pause")

    def stop_simulation(self):
        """Stop the simulation"""
        self.running = False
        self.paused = False
        self.run_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)

    def check_queue(self):
        """Check the message queue for updates"""
        try:
            while True:
                message_type, data = self.message_queue.get_nowait()
                if message_type == "update_explanation":
                    self.output_text.insert(tk.END, data + "\n")
                    self.output_text.see(tk.END)
                elif message_type == "update_tree":
                    self.visualization.update(data)
                elif message_type == "update_progress":
                    self.progress["value"] = data
                elif message_type == "simulation_finished":
                    self.stop_simulation()
                    self.output_text.insert(tk.END, "Simulation finished.\n")
                    self.output_text.see(tk.END)
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)

    def run(self):
        """Run the application"""
        self.root.mainloop()
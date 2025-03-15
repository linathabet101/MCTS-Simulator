import tkinter as tk
import math

class Visualization:
    def __init__(self, canvas):
        self.canvas = canvas
        self.node_size = 30
        self.level_spacing = 120  # Increased vertical spacing
        self.node_spacing = 80  # Horizontal spacing between nodes
        self.node_colors = {
            "root": "#4CAF50",  # Green for root
            "best_path": "#FF5722",  # Orange for best path
            "expanded": "#2196F3",  # Blue for expanded nodes
            "leaf": "#9C27B0",  # Purple for leaf nodes
            "default": "#607D8B"  # Grey for other nodes
        }
        self.zoom = 1.0
        self.canvas_width = 1200  # Default canvas width
        self.canvas_height = 800  # Default canvas height

    def update(self, root):
        """Update the visualization with the current tree."""
        # Clear the canvas
        self.canvas.delete("all")
        
        # Calculate tree depth and width
        max_depth, node_counts = self._analyze_tree(root)
        
        # Adjust canvas size if needed
        self._adjust_canvas_size(max_depth, max(node_counts.values()) if node_counts else 1)
        
        # Draw tree
        center_x = self.canvas_width / 2
        self._draw_node(root, center_x, 50, 0, node_counts)
        
        # Update canvas scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _analyze_tree(self, node, depth=0, node_counts=None):
        """Analyze the tree to determine its depth and width at each level."""
        if node_counts is None:
            node_counts = {}
            
        # Update count for this depth level
        if depth not in node_counts:
            node_counts[depth] = 0
        node_counts[depth] += 1
        
        # Recursively analyze children
        max_depth = depth
        for child in node.children:
            child_depth, _ = self._analyze_tree(child, depth + 1, node_counts)
            max_depth = max(max_depth, child_depth)
            
        return max_depth, node_counts
    
    def _adjust_canvas_size(self, depth, max_width):
        """Adjust canvas size based on tree dimensions."""
        min_width = max(1200, max_width * self.node_spacing)
        min_height = max(800, (depth + 1) * self.level_spacing)
        
        self.canvas_width = min_width
        self.canvas_height = min_height
    
    def _draw_node(self, node, x, y, depth, node_counts, is_best_path=False):
        """Draw a node and its children recursively."""
        if node is None:
            return
            
        # Determine node color
        if node.parent is None:  # Root node
            color = self.node_colors["root"]
        elif is_best_path:
            color = self.node_colors["best_path"]
        elif not node.children:  # Leaf node
            color = self.node_colors["leaf"]
        elif node.visits > 5:  # Frequently visited node
            color = self.node_colors["expanded"]
        else:
            color = self.node_colors["default"]
        
        # Draw the node circle
        node_id = self.canvas.create_oval(
            x - self.node_size, y - self.node_size,
            x + self.node_size, y + self.node_size,
            fill=color, outline="black", width=2
        )
        
        # Add text inside the node
        visit_ratio = 0 if node.visits == 0 else node.value / node.visits
        
        self.canvas.create_text(
            x, y - 8,
            text=f"V: {visit_ratio:.2f}",
            font=("Arial", 8),
            fill="white"
        )
        
        self.canvas.create_text(
            x, y + 8,
            text=f"N: {node.visits}",
            font=("Arial", 8),
            fill="white"
        )
        
        # Find best child for highlighting the path
        best_child = None
        if node.children:
            best_child = max(node.children, key=lambda c: c.visits) if node.children else None
        
        # Calculate positions for child nodes
        if node.children:
            num_children = len(node.children)
            total_width = max(self.canvas_width, num_children * self.node_spacing)
            
            if num_children == 1:
                # Single child - place directly below parent
                child_x = x
                child = node.children[0]
                child_y = y + self.level_spacing
                
                # Draw connection line
                self.canvas.create_line(
                    x, y + self.node_size,
                    child_x, child_y - self.node_size,
                    width=2, fill="black"
                )
                
                # Recursively draw the child
                self._draw_node(
                    child, child_x, child_y, depth + 1, 
                    node_counts, is_best_path=(child == best_child)
                )
            else:
                # Multiple children - distribute evenly
                child_slots = num_children
                width_per_child = total_width / (child_slots + 1)
                
                for i, child in enumerate(node.children):
                    # Calculate child position
                    child_x = (i + 1) * width_per_child
                    child_y = y + self.level_spacing
                    
                    # Draw connection line
                    self.canvas.create_line(
                        x, y + self.node_size,
                        child_x, child_y - self.node_size,
                        width=2, fill="black"
                    )
                    
                    # Recursively draw the child
                    self._draw_node(
                        child, child_x, child_y, depth + 1, 
                        node_counts, is_best_path=(child == best_child)
                    )
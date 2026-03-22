"""
Visualization module for swarm robotics simulation.
Handles real-time animated visualization of swarm exploration.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
from matplotlib.collections import PatchCollection
from typing import List, Tuple
from .environment import Environment, Obstacle
from .robot import Robot
from .swarm import RobotSwarm


class SwarmVisualizer:
    """
    Handles visualization and animation of swarm robotics simulation.
    """
    
    def __init__(self, swarm: RobotSwarm, environment: Environment,
                 figsize: Tuple[int, int] = (14, 7)):
        """
        Initialize visualizer.
        
        Args:
            swarm: RobotSwarm object
            environment: Environment object
            figsize: Figure size (width, height)
        """
        self.swarm = swarm
        self.environment = environment
        
        # Create figure and axes
        self.fig, (self.ax_main, self.ax_info) = plt.subplots(
            1, 2, figsize=figsize,
            gridspec_kw={'width_ratios': [3, 1]}
        )
        
        # Main visualization setup
        self.ax_main.set_xlim(0, environment.width)
        self.ax_main.set_ylim(0, environment.height)
        self.ax_main.set_aspect('equal')
        self.ax_main.set_title('Swarm Robotics Path Planning and Exploration')
        self.ax_main.set_xlabel('X Position')
        self.ax_main.set_ylabel('Y Position')
        self.ax_main.grid(True, alpha=0.3)
        
        # Info panel setup
        self.ax_info.axis('off')
        
        # Artists for animation
        self.robot_scatter = None
        self.velocity_quiver = None
        self.obstacle_patches = []
        self.target_circle = None
        self.exploration_heatmap = None
        self.info_text = None
        
        # Data storage for analysis
        self.history = {
            'iterations': [],
            'best_fitness': [],
            'exploration_coverage': [],
            'robots_near_target': [],
            'avg_speed': []
        }
        
        self._setup_static_elements()
    
    def _setup_static_elements(self):
        """Setup static elements (obstacles, target) on the main axis."""
        # Draw obstacles
        for obstacle in self.environment.obstacles:
            circle = patches.Circle(
                (obstacle.x, obstacle.y),
                obstacle.radius,
                color='gray',
                alpha=0.5,
                zorder=3
            )
            self.ax_main.add_patch(circle)
        
        # Draw target
        self.target_circle = patches.Circle(
            (self.environment.target_x, self.environment.target_y),
            5.0,
            color='red',
            alpha=0.7,
            label='Target',
            zorder=4
        )
        self.ax_main.add_patch(self.target_circle)
        
        # Add legend
        self.ax_main.legend(loc='upper left')
    
    def update_frame(self, step_data: dict):
        """
        Update visualization for current frame.
        
        Args:
            step_data: Dictionary with current step statistics
        """
        # Clear previous artists (except static elements)
        if self.robot_scatter:
            self.robot_scatter.remove()
        if self.velocity_quiver:
            self.velocity_quiver.remove()
        
        # Update history
        self.history['iterations'].append(step_data['iteration'])
        self.history['best_fitness'].append(step_data['best_fitness'])
        self.history['exploration_coverage'].append(step_data['exploration_coverage'])
        self.history['robots_near_target'].append(step_data['robots_near_target'])
        self.history['avg_speed'].append(step_data['avg_robot_speed'])
        
        # Plot robots
        positions = self.swarm.get_robot_positions()
        if positions:
            xs, ys = zip(*positions)
            self.robot_scatter = self.ax_main.scatter(
                xs, ys, c='blue', s=100, alpha=0.6,
                label='Robots', zorder=5
            )
        
        # Plot velocities as quiver (optional, can be disabled for clarity)
        velocities = self.swarm.get_robot_velocities()
        if velocities and np.random.rand() > 0.7:  # Show every 30% of updates
            vxs, vys = zip(*velocities)
            self.velocity_quiver = self.ax_main.quiver(
                xs, ys, vxs, vys,
                color='cyan', alpha=0.5, scale=50, zorder=4
            )
        
        # Update swarm center
        center_x, center_y = self.swarm.get_swarm_center()
        self.ax_main.plot(center_x, center_y, 'b*', markersize=15, 
                         label='Swarm Center', zorder=6)
        
        # Update info panel
        self._update_info_panel(step_data)
        
        return self.robot_scatter, self.velocity_quiver
    
    def _update_info_panel(self, step_data: dict):
        """Update information text panel."""
        if self.info_text:
            self.info_text.remove()
        
        # Format info text
        info_str = (
            f"Iteration: {step_data['iteration']}\n"
            f"Best Fitness: {step_data['best_fitness']:.2f}\n"
            f"Exploration: {step_data['exploration_coverage']:.1f}%\n"
            f"Robots Near Target: {step_data['robots_near_target']}\n"
            f"Avg Speed: {step_data['avg_robot_speed']:.2f}\n"
            f"Swarm Spread: {self.swarm.get_swarm_spread():.2f}\n"
            f"Global Best: ({step_data['global_best_pos'][0]:.1f}, "
            f"{step_data['global_best_pos'][1]:.1f})\n"
        )
        
        if step_data['target_found']:
            info_str += "\n✓ TARGET FOUND!"
        
        self.info_text = self.ax_info.text(
            0.1, 0.95, info_str,
            transform=self.ax_info.transAxes,
            fontsize=10,
            verticalalignment='top',
            family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )
    
    def create_animation(self, simulation_data: List[dict], 
                        interval: int = 100) -> animation.FuncAnimation:
        """
        Create animation from simulation data.
        
        Args:
            simulation_data: List of step data dictionaries
            interval: Animation interval in milliseconds
            
        Returns:
            FuncAnimation object
        """
        def animate(frame):
            if frame < len(simulation_data):
                self.update_frame(simulation_data[frame])
            return self.robot_scatter, self.velocity_quiver
        
        return animation.FuncAnimation(
            self.fig, animate,
            frames=len(simulation_data),
            interval=interval,
            blit=False,
            repeat=True
        )
    
    def show_static(self, step_data: dict):
        """Display a single static frame (non-animated)."""
        self.update_frame(step_data)
        plt.tight_layout()
        plt.show()
    
    def save_animation(self, simulation_data: List[dict], 
                       filename: str, interval: int = 100, fps: int = 10):
        """
        Save animation to file.
        
        Args:
            simulation_data: List of step data dictionaries
            filename: Output filename (e.g., 'simulation.mp4')
            interval: Animation interval in milliseconds
            fps: Frames per second for output
        """
        anim = self.create_animation(simulation_data, interval)
        
        # Save animation
        if filename.endswith('.gif'):
            anim.save(filename, writer='pillow', fps=fps)
        else:
            anim.save(filename, fps=fps)
        
        print(f"Animation saved to {filename}")
    
    def plot_convergence(self):
        """Plot convergence metrics."""
        if not self.history['iterations']:
            print("No data to plot")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # Best fitness
        axes[0, 0].plot(self.history['iterations'], self.history['best_fitness'])
        axes[0, 0].set_title('Best Fitness Over Time')
        axes[0, 0].set_xlabel('Iteration')
        axes[0, 0].set_ylabel('Fitness')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Exploration coverage
        axes[0, 1].plot(self.history['iterations'], self.history['exploration_coverage'])
        axes[0, 1].set_title('Exploration Coverage')
        axes[0, 1].set_xlabel('Iteration')
        axes[0, 1].set_ylabel('Coverage (%)')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Robots near target
        axes[1, 0].bar(self.history['iterations'][::10], 
                      self.history['robots_near_target'][::10])
        axes[1, 0].set_title('Robots Near Target')
        axes[1, 0].set_xlabel('Iteration')
        axes[1, 0].set_ylabel('Count')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Average speed
        axes[1, 1].plot(self.history['iterations'], self.history['avg_speed'])
        axes[1, 1].set_title('Average Swarm Speed')
        axes[1, 1].set_xlabel('Iteration')
        axes[1, 1].set_ylabel('Speed')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

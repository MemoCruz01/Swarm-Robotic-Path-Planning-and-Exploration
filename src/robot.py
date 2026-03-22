"""
Robot agent module for swarm robotics simulation.
Represents individual robots with position, velocity, and sensing.
"""

import numpy as np
from typing import Tuple


class Robot:
    """
    Represents an individual robot in the swarm.
    """
    
    def __init__(self, robot_id: int, x: float, y: float, 
                 max_speed: float = 2.0, sensor_range: float = 15.0):
        """
        Initialize a robot.
        
        Args:
            robot_id: Unique robot identifier
            x: Initial x position
            y: Initial y position
            max_speed: Maximum movement speed per iteration
            sensor_range: Sensing range for environment detection
        """
        self.id = robot_id
        self.x = x
        self.y = y
        self.vx = 0.0  # Velocity x
        self.vy = 0.0  # Velocity y
        self.max_speed = max_speed
        self.sensor_range = sensor_range
        
        # Best position discovered by this robot
        self.best_x = x
        self.best_y = y
        self.best_fitness = float('-inf')
        
        # Collision avoidance
        self.angle = np.random.uniform(0, 2 * np.pi)
        self.target_x = x
        self.target_y = y
        self.exploration_urge = 1.0
    
    def update_velocity(self, best_x: float, best_y: float, 
                       global_best_x: float, global_best_y: float,
                       w: float = 0.7298, c1: float = 1.49618, 
                       c2: float = 1.49618):
        """
        Update velocity using PSO update rule.
        
        Args:
            best_x: Robot's best position x
            best_y: Robot's best position y
            global_best_x: Swarm's global best position x
            global_best_y: Swarm's global best position y
            w: Inertia weight
            c1: Cognitive parameter
            c2: Social parameter
        """
        r1 = np.random.uniform(0, 1)
        r2 = np.random.uniform(0, 1)
        
        # PSO velocity update
        self.vx = (w * self.vx + 
                   c1 * r1 * (best_x - self.x) + 
                   c2 * r2 * (global_best_x - self.x))
        
        self.vy = (w * self.vy + 
                   c1 * r1 * (best_y - self.y) + 
                   c2 * r2 * (global_best_y - self.y))
        
        # Limit speed
        speed = np.sqrt(self.vx**2 + self.vy**2)
        if speed > self.max_speed:
            self.vx = (self.vx / speed) * self.max_speed
            self.vy = (self.vy / speed) * self.max_speed
    
    def update_position(self):
        """Update robot position based on velocity."""
        self.x += self.vx
        self.y += self.vy
        self.angle = np.arctan2(self.vy, self.vx)
    
    def enforce_bounds(self, width: float, height: float, boundary_margin: float = 1.0):
        """
        Enforce environment boundaries and bounce if out of bounds.
        
        Args:
            width: Environment width
            height: Environment height
            boundary_margin: Margin from boundary
        """
        if self.x < boundary_margin:
            self.x = boundary_margin
            self.vx = abs(self.vx)
        elif self.x > width - boundary_margin:
            self.x = width - boundary_margin
            self.vx = -abs(self.vx)
        
        if self.y < boundary_margin:
            self.y = boundary_margin
            self.vy = abs(self.vy)
        elif self.y > height - boundary_margin:
            self.y = height - boundary_margin
            self.vy = -abs(self.vy)
    
    def avoid_obstacle(self, obstacle_x: float, obstacle_y: float, 
                      obstacle_radius: float, min_safe_distance: float = 5.0):
        """
        Adjust velocity to avoid obstacle with stronger repulsion.
        
        Args:
            obstacle_x: Obstacle center x
            obstacle_y: Obstacle center y
            obstacle_radius: Obstacle radius
            min_safe_distance: Minimum safe distance from obstacle
        """
        dx = self.x - obstacle_x
        dy = self.y - obstacle_y
        distance = np.sqrt(dx**2 + dy**2)
        safe_zone = min_safe_distance + obstacle_radius
        
        # Strong repulsion when close to obstacle
        if distance < safe_zone:
            if distance < 0.1:
                distance = 0.1  # Avoid division by zero
            
            # Calculate repulsion strength based on proximity
            # Closer = stronger repulsion
            repel_strength = max(1.0, (safe_zone - distance) / safe_zone * 3.0)
            
            self.vx += (dx / distance) * repel_strength
            self.vy += (dy / distance) * repel_strength
    
    def predict_collision(self, obstacles: list, safety_radius: float = 2.0) -> bool:
        """
        Predict if the next move will result in collision.
        
        Args:
            obstacles: List of Obstacle objects
            safety_radius: Safety buffer
            
        Returns:
            True if collision predicted
        """
        next_x = self.x + self.vx
        next_y = self.y + self.vy
        
        for obs in obstacles:
            dist_to_obs = np.sqrt((next_x - obs.x)**2 + (next_y - obs.y)**2)
            if dist_to_obs < (obs.radius + safety_radius):
                return True
        
        return False
    
    def correct_position(self, obstacles: list, boundary_min: float = 0, 
                        boundary_max_x: float = 100, boundary_max_y: float = 100):
        """
        If position is inside an obstacle, move robot out and reverse velocity.
        
        Args:
            obstacles: List of Obstacle objects
            boundary_min: Minimum boundary coordinate
            boundary_max_x: Maximum x boundary
            boundary_max_y: Maximum y boundary
        """
        for obs in obstacles:
            dist_to_obs = np.sqrt((self.x - obs.x)**2 + (self.y - obs.y)**2)
            
            # If inside obstacle, bounce out
            if dist_to_obs < obs.radius:
                # Calculate direction away from obstacle
                if dist_to_obs < 0.1:
                    dist_to_obs = 0.1
                
                dx = self.x - obs.x
                dy = self.y - obs.y
                
                # Push robot outside obstacle
                push_distance = obs.radius + 2.0
                self.x = obs.x + (dx / dist_to_obs) * push_distance
                self.y = obs.y + (dy / dist_to_obs) * push_distance
                
                # Reverse and dampen velocity (bounce effect)
                self.vx *= -0.5
                self.vy *= -0.5
    
    def update_best_position(self, fitness: float):
        """
        Update robot's best position if current fitness is better.
        
        Args:
            fitness: Current fitness value
        """
        if fitness > self.best_fitness:
            self.best_fitness = fitness
            self.best_x = self.x
            self.best_y = self.y
    
    def set_exploration_target(self, target_x: float, target_y: float):
        """Set a target for exploration."""
        self.target_x = target_x
        self.target_y = target_y
    
    def get_position(self) -> Tuple[float, float]:
        """Get current position."""
        return self.x, self.y
    
    def get_velocity(self) -> Tuple[float, float]:
        """Get current velocity."""
        return self.vx, self.vy
    
    def distance_to(self, x: float, y: float) -> float:
        """Calculate distance to a point."""
        return np.sqrt((self.x - x)**2 + (self.y - y)**2)

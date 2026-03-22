"""
Environment module for swarm robotics simulation.
Handles obstacles, target location, and boundary constraints.
"""

import numpy as np
from typing import List, Tuple


class Obstacle:
    """Represents a circular obstacle in the environment."""
    
    def __init__(self, x: float, y: float, radius: float):
        self.x = x
        self.y = y
        self.radius = radius
    
    def distance_to_point(self, x: float, y: float) -> float:
        """Calculate distance from point to obstacle center."""
        return np.sqrt((self.x - x)**2 + (self.y - y)**2)
    
    def is_collision(self, x: float, y: float, safety_radius: float = 0.0) -> bool:
        """Check if point collides with obstacle."""
        return self.distance_to_point(x, y) <= (self.radius + safety_radius)


class Environment:
    """
    Represents the simulation environment with obstacles and targets.
    """
    
    def __init__(self, width: float, height: float, 
                 obstacles: List[Obstacle] = None,
                 target_x: float = None, target_y: float = None):
        """
        Initialize the environment.
        
        Args:
            width: Environment width
            height: Environment height
            obstacles: List of Obstacle objects
            target_x: Target x position
            target_y: Target y position
        """
        self.width = width
        self.height = height
        self.obstacles = obstacles if obstacles else []
        self.target_x = target_x if target_x is not None else width - 10
        self.target_y = target_y if target_y is not None else height - 10
        self.visited_regions = set()  # Track explored regions
    
    def is_valid_position(self, x: float, y: float, safety_radius: float = 0.0) -> bool:
        """
        Check if position is valid (within bounds and no collision).
        
        Args:
            x: X coordinate
            y: Y coordinate
            safety_radius: Safety buffer around position
            
        Returns:
            True if position is valid
        """
        # Check bounds
        if x - safety_radius < 0 or x + safety_radius > self.width:
            return False
        if y - safety_radius < 0 or y + safety_radius > self.height:
            return False
        
        # Check obstacles
        for obstacle in self.obstacles:
            if obstacle.is_collision(x, y, safety_radius):
                return False
        
        return True
    
    def get_nearest_obstacle(self, x: float, y: float) -> Tuple[float, Obstacle]:
        """
        Get the nearest obstacle and its distance.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Tuple of (distance, obstacle)
        """
        if not self.obstacles:
            return float('inf'), None
        
        distances = [(obs.distance_to_point(x, y), obs) for obs in self.obstacles]
        return min(distances, key=lambda d: d[0])
    
    def get_obstacles_in_range(self, x: float, y: float, 
                               sensor_range: float) -> List[Obstacle]:
        """
        Get all obstacles within sensor range.
        
        Args:
            x: X coordinate
            y: Y coordinate
            sensor_range: Sensing range
            
        Returns:
            List of obstacles within range
        """
        nearby = []
        for obs in self.obstacles:
            if obs.distance_to_point(x, y) <= sensor_range:
                nearby.append(obs)
        return nearby
    
    def distance_to_target(self, x: float, y: float) -> float:
        """Calculate distance to target."""
        return np.sqrt((self.target_x - x)**2 + (self.target_y - y)**2)
    
    def is_reached_target(self, x: float, y: float, radius: float = 5.0) -> bool:
        """Check if position has reached target."""
        return self.distance_to_target(x, y) <= radius
    
    def record_exploration(self, x: float, y: float, grid_size: float = 2.0):
        """Record that a region has been explored."""
        grid_x = int(x / grid_size)
        grid_y = int(y / grid_size)
        self.visited_regions.add((grid_x, grid_y))
    
    def get_exploration_coverage(self) -> float:
        """Get percentage of environment that has been explored."""
        total_regions = int(self.width / 2.0) * int(self.height / 2.0)
        if total_regions == 0:
            return 0.0
        return min(100.0, (len(self.visited_regions) / total_regions) * 100)

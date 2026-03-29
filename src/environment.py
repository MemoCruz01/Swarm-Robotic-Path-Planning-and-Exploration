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
        
        # Phase 4: Environment Complexity
        self.terrain_system = None
        self.dynamic_obstacles = None
        self.phase4_enabled = False
        
        # Initialize Phase 4 systems if enabled
        try:
            from config.realism_settings import ENABLE_PHASE4_ENVIRONMENT, TERRAIN_ENABLED, DYNAMIC_OBSTACLES
            if ENABLE_PHASE4_ENVIRONMENT:
                self.phase4_enabled = True
                
                if TERRAIN_ENABLED:
                    from .terrain_system import TerrainSystem
                    self.terrain_system = TerrainSystem(width, height)
                
                if DYNAMIC_OBSTACLES:
                    from .dynamic_obstacles import DynamicObstacleManager
                    self.dynamic_obstacles = DynamicObstacleManager(width, height)
        except Exception as e:
            # Phase 4 not available (missing dependencies)
            pass
    
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
    
    def check_robot_collisions(self, robots: List, 
                               robot_radius: float = 1.0,
                               elasticity: float = 0.7,
                               separation_speed: float = 0.3) -> int:
        """
        Detect and resolve all robot-robot collisions.
        
        Args:
            robots: List of robot objects
            robot_radius: Radius of each robot for collision detection
            elasticity: Bounce factor (0=stick, 0.7=bounce, 1.0=perfect)
            separation_speed: Factor for separation force
            
        Returns:
            Number of collisions resolved
        """
        collision_count = 0
        collision_distance = 2.0 * robot_radius
        
        # Check all pairs of robots
        for i in range(len(robots)):
            for j in range(i + 1, len(robots)):
                robot1 = robots[i]
                robot2 = robots[j]
                
                # Calculate distance between robot centers
                dx = robot2.x - robot1.x
                dy = robot2.y - robot1.y
                dist = np.sqrt(dx**2 + dy**2)
                
                # Check if collision
                if dist < collision_distance and dist > 0:
                    collision_count += 1
                    
                    # Resolve collision
                    self._resolve_robot_collision(
                        robot1, robot2, dx, dy, dist,
                        collision_distance, elasticity, separation_speed
                    )
        
        return collision_count
    
    def _resolve_robot_collision(self, robot1, robot2, 
                                 dx: float, dy: float, 
                                 dist: float,
                                 collision_distance: float,
                                 elasticity: float = 0.7,
                                 separation_speed: float = 0.3):
        """
        Resolve a single collision between two robots.
        
        Args:
            robot1: First robot
            robot2: Second robot
            dx: Relative x position (robot2 - robot1)
            dy: Relative y position (robot2 - robot1)
            dist: Distance between centers
            collision_distance: Threshold for collision
            elasticity: Bounce factor
            separation_speed: Separation force scale
        """
        # Normal vector (pointing from robot1 to robot2)
        normal_x = dx / dist
        normal_y = dy / dist
        
        # Separation: push robots apart
        overlap = collision_distance - dist
        separation = overlap * separation_speed / 2.0
        
        robot1.x -= normal_x * separation
        robot1.y -= normal_y * separation
        robot2.x += normal_x * separation
        robot2.y += normal_y * separation
        
        # Velocity response: bouncy reflection
        # Reverse velocities with elasticity dampening
        robot1.v_left *= -elasticity
        robot1.v_right *= -elasticity
        robot2.v_left *= -elasticity
        robot2.v_right *= -elasticity

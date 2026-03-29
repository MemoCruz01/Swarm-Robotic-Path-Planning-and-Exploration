"""
Dynamic Obstacles System - Moving environmental hazards.

Manages dynamically moving obstacles that can:
- Move with constant velocity
- Rotate/spin
- Spawn and despawn based on distance from swarm
- Predict trajectory for collision avoidance

DWA uses predicted positions to avoid collisions before they happen.

Created: March 29, 2026
Version: 1.0 (Phase 4 - Environment Complexity)
"""

import numpy as np
from config.realism_settings import (
    DYNAMIC_OBSTACLE_MIN_SPEED,
    DYNAMIC_OBSTACLE_MAX_SPEED,
    DYNAMIC_OBSTACLE_ROTATION_SPEED,
    DYNAMIC_OBSTACLE_PREDICTION_STEPS,
    DYNAMIC_OBSTACLE_SPAWN_DISTANCE,
    DYNAMIC_OBSTACLE_DESPAWN_DISTANCE,
    DEBUG_PHASE4,
)


class DynamicObstacle:
    """
    Represents a moving/rotating obstacle.
    """
    
    def __init__(self, obstacle_id: int, x: float, y: float, 
                 radius: float, vx: float = 0.0, vy: float = 0.0,
                 rotation_speed: float = 0.0):
        """
        Initialize dynamic obstacle.
        
        Args:
            obstacle_id: Unique identifier
            x, y: Initial position
            radius: Collision radius
            vx, vy: Velocity components
            rotation_speed: Angular velocity (rad/step)
        """
        self.id = obstacle_id
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = vx
        self.vy = vy
        self.rotation_speed = rotation_speed
        self.theta = np.random.uniform(0, 2 * np.pi)  # Orientation
        
        # Lifetime management
        self.alive = True
        self.age = 0
    
    def update(self, environment_width: float, environment_height: float,
               despawn_distance: float, swarm_center: tuple = None):
        """
        Update obstacle position and check bounds.
        
        Args:
            environment_width: Environment width
            environment_height: Environment height
            despawn_distance: Distance threshold for despawning
            swarm_center: Swarm center position (for despawn check)
        """
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Update rotation
        self.theta += self.rotation_speed
        self.theta = self.theta % (2 * np.pi)
        
        # Bounce off walls (simple boundary reflection)
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = abs(self.vx)
        elif self.x + self.radius > environment_width:
            self.x = environment_width - self.radius
            self.vx = -abs(self.vx)
        
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy = abs(self.vy)
        elif self.y + self.radius > environment_height:
            self.y = environment_height - self.radius
            self.vy = -abs(self.vy)
        
        # Check despawning
        if swarm_center is not None:
            dist_to_swarm = np.sqrt((self.x - swarm_center[0])**2 + 
                                   (self.y - swarm_center[1])**2)
            if dist_to_swarm > despawn_distance:
                self.alive = False
        
        self.age += 1
    
    def predict_position(self, steps: int = 1) -> tuple:
        """
        Predict obstacle position N steps in the future.
        
        Args:
            steps: Number of steps to predict
            
        Returns:
            (x, y) predicted position
        """
        pred_x = self.x + self.vx * steps
        pred_y = self.y + self.vy * steps
        return (pred_x, pred_y)
    
    def predict_trajectory(self, steps: int = None) -> list:
        """
        Predict complete trajectory.
        
        Args:
            steps: Number of steps (defaults to DYNAMIC_OBSTACLE_PREDICTION_STEPS)
            
        Returns:
            List of (x, y) positions
        """
        if steps is None:
            steps = DYNAMIC_OBSTACLE_PREDICTION_STEPS
        
        trajectory = [(self.x, self.y)]
        x, y = self.x, self.y
        
        for _ in range(steps):
            x += self.vx
            y += self.vy
            trajectory.append((x, y))
        
        return trajectory
    
    def distance_to(self, x: float, y: float) -> float:
        """Distance from point to obstacle center."""
        return np.sqrt((self.x - x)**2 + (self.y - y)**2)
    
    def is_collision(self, x: float, y: float, collision_radius: float = 0.0) -> bool:
        """
        Check collision with point.
        
        Args:
            x, y: Point position
            collision_radius: Extra collision margin
            
        Returns:
            True if collision detected
        """
        return self.distance_to(x, y) <= (self.radius + collision_radius)


class DynamicObstacleManager:
    """
    Manages a population of dynamic obstacles.
    Handles spawning, despawning, and updates.
    """
    
    def __init__(self, environment_width: float, environment_height: float):
        """
        Initialize manager.
        
        Args:
            environment_width: Environment width
            environment_height: Environment height
        """
        self.width = environment_width
        self.height = environment_height
        self.obstacles = []
        self.next_id = 0
    
    def spawn_random_obstacle(self, min_distance: float = 50) -> DynamicObstacle:
        """
        Spawn new obstacle at random position.
        
        Args:
            min_distance: Minimum distance from origin
            
        Returns:
            New DynamicObstacle
        """
        angle = np.random.uniform(0, 2 * np.pi)
        distance = np.random.uniform(min_distance, min_distance + 20)
        x = self.width / 2 + distance * np.cos(angle)
        y = self.height / 2 + distance * np.sin(angle)
        
        # Clamp to bounds
        x = max(5, min(self.width - 5, x))
        y = max(5, min(self.height - 5, y))
        
        radius = np.random.uniform(3, 7)
        
        # Random velocity
        speed = np.random.uniform(DYNAMIC_OBSTACLE_MIN_SPEED, DYNAMIC_OBSTACLE_MAX_SPEED)
        heading = np.random.uniform(0, 2 * np.pi)
        vx = speed * np.cos(heading)
        vy = speed * np.sin(heading)
        
        # Occasional rotation
        rotation_speed = DYNAMIC_OBSTACLE_ROTATION_SPEED if np.random.random() < 0.5 else 0.0
        
        obs = DynamicObstacle(
            self.next_id, x, y, radius, vx, vy, rotation_speed
        )
        self.next_id += 1
        self.obstacles.append(obs)
        
        if DEBUG_PHASE4:
            print(f"  [SPAWN] Dynamic obstacle #{obs.id} at ({x:.1f}, {y:.1f}), speed={speed:.2f}")
        
        return obs
    
    def update_all(self, swarm_center: tuple):
        """
        Update all obstacles and manage lifecycle.
        
        Args:
            swarm_center: Swarm center position for distance calculations
        """
        for obs in self.obstacles:
            obs.update(
                self.width,
                self.height,
                DYNAMIC_OBSTACLE_DESPAWN_DISTANCE,
                swarm_center
            )
        
        # Remove dead obstacles
        alive_before = len(self.obstacles)
        self.obstacles = [obs for obs in self.obstacles if obs.alive]
        
        if len(self.obstacles) < alive_before and DEBUG_PHASE4:
            print(f"  [DESPAWN] {alive_before - len(self.obstacles)} obstacles removed")
    
    def get_nearby_obstacles(self, x: float, y: float, distance: float) -> list:
        """
        Get obstacles near a position.
        
        Args:
            x, y: Query position
            distance: Search radius
            
        Returns:
            List of nearby DynamicObstacle objects
        """
        nearby = []
        for obs in self.obstacles:
            if obs.distance_to(x, y) <= distance:
                nearby.append(obs)
        return nearby
    
    def get_collision_obstacles(self, x: float, y: float, margin: float = 0.0) -> list:
        """
        Get obstacles in collision at position.
        
        Args:
            x, y: Query position
            margin: Extra collision margin
            
        Returns:
            List of colliding obstacles
        """
        colliding = []
        for obs in self.obstacles:
            if obs.is_collision(x, y, margin):
                colliding.append(obs)
        return colliding
    
    def get_all_trajectories(self, steps: int = None) -> list:
        """
        Get predicted trajectories for all obstacles.
        
        Args:
            steps: Number of prediction steps
            
        Returns:
            List of trajectories (each trajectory is list of positions)
        """
        trajectories = []
        for obs in self.obstacles:
            trajectories.append(obs.predict_trajectory(steps))
        return trajectories
    
    def get_statistics(self) -> dict:
        """Get obstacle manager statistics."""
        if not self.obstacles:
            return {
                'total_obstacles': 0,
                'avg_speed': 0.0,
                'avg_rotation': 0.0,
            }
        
        speeds = [np.sqrt(obs.vx**2 + obs.vy**2) for obs in self.obstacles]
        rotations = [abs(obs.rotation_speed) for obs in self.obstacles]
        
        return {
            'total_obstacles': len(self.obstacles),
            'avg_speed': np.mean(speeds),
            'avg_rotation': np.mean(rotations),
            'max_speed': max(speeds),
            'oldest_age': max(obs.age for obs in self.obstacles),
        }

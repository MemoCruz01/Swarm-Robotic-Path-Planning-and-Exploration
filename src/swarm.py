"""
Swarm management module for coordinating multiple robots.
"""

import numpy as np
from typing import List
from .robot import Robot
from .environment import Environment, Obstacle
from .pso import PSO


class RobotSwarm:
    """
    Manages a swarm of robots performing collective exploration and path planning.
    """
    
    def __init__(self, num_robots: int, 
                 environment: Environment,
                 robot_speed: float = 2.0,
                 sensor_range: float = 15.0):
        """
        Initialize robot swarm.
        
        Args:
            num_robots: Number of robots in swarm
            environment: Environment object
            robot_speed: Maximum speed for each robot
            sensor_range: Sensing range for each robot
        """
        self.num_robots = num_robots
        self.environment = environment
        self.robot_speed = robot_speed
        self.sensor_range = sensor_range
        
        # Initialize robots at random positions
        self.robots = self._create_robots()
        
        # Initialize PSO algorithm
        self.pso = PSO(num_robots)
        
        # Statistics
        self.iteration = 0
        self.target_found = False
        self.target_found_iteration = None
    
    def _create_robots(self) -> List[Robot]:
        """
        Create robot population with random initial positions.
        
        Returns:
            List of Robot objects
        """
        robots = []
        for i in range(self.num_robots):
            # Random valid starting position
            while True:
                x = np.random.uniform(5, self.environment.width - 5)
                y = np.random.uniform(5, self.environment.height - 5)
                
                if self.environment.is_valid_position(x, y, safety_radius=2.0):
                    break
            
            robot = Robot(i, x, y, self.robot_speed, self.sensor_range)
            robots.append(robot)
        
        return robots
    
    def step(self) -> dict:
        """
        Execute one simulation step for the entire swarm.
        
        Returns:
            Dictionary with step statistics
        """
        # Run PSO update
        target_reached = self.pso.update_swarm(self.robots, self.environment)
        
        # Apply advanced collision avoidance
        for robot in self.robots:
            # Predictive collision detection - check if next move will collide
            if robot.predict_collision(self.environment.obstacles, safety_radius=3.0):
                # Manually apply repulsion from nearby obstacles
                nearby_obstacles = self.environment.get_obstacles_in_range(
                    robot.x, robot.y, robot.sensor_range + 10.0
                )
                for obs in nearby_obstacles:
                    robot.avoid_obstacle(obs.x, obs.y, obs.radius, min_safe_distance=8.0)
            
            # Update position
            robot.update_position()
            
            # Correct position if collision occurred (safety net)
            robot.correct_position(
                self.environment.obstacles,
                boundary_min=0,
                boundary_max_x=self.environment.width,
                boundary_max_y=self.environment.height
            )
            
            # Enforce boundaries
            robot.enforce_bounds(self.environment.width, self.environment.height)
            
            # Record exploration
            self.environment.record_exploration(robot.x, robot.y)
        
        # Check stopping conditions
        self._check_target_reached()
        
        # Compile statistics
        stats = {
            'iteration': self.iteration,
            'best_fitness': self.pso.global_best_fitness,
            'exploration_coverage': self.environment.get_exploration_coverage(),
            'target_found': self.target_found,
            'robots_near_target': self._count_robots_near_target(),
            'global_best_pos': self.pso.get_global_best(),
            'avg_robot_speed': self._get_avg_robot_speed(),
        }
        
        self.iteration += 1
        return stats
    
    def _check_target_reached(self):
        """
        Check if simulation should stop based on target conditions.
        Uses settings from config to determine stopping criteria.
        """
        from config.settings import (
            STOP_ON_SINGLE_ROBOT, 
            STOP_ON_ALL_ROBOTS,
            STOP_ON_PERCENTAGE,
            TARGET_ROBOT_PERCENTAGE,
            TARGET_RADIUS
        )
        
        robots_in_target = self._count_robots_near_target(radius=TARGET_RADIUS)
        total_robots = len(self.robots)
        
        # Check stopping condition 1: Stop on first robot
        if STOP_ON_SINGLE_ROBOT and robots_in_target >= 1:
            if not self.target_found:
                self.target_found = True
                self.target_found_iteration = self.iteration
                print(f"\n✓ CONDITION MET: First robot reached target!")
        
        # Check stopping condition 2: Stop when all robots in target
        elif STOP_ON_ALL_ROBOTS and robots_in_target >= total_robots:
            if not self.target_found:
                self.target_found = True
                self.target_found_iteration = self.iteration
                print(f"\n✓ CONDITION MET: All {total_robots} robots reached target!")
        
        # Check stopping condition 3: Stop when X% of robots in target
        elif STOP_ON_PERCENTAGE:
            required_robots = max(1, int(total_robots * TARGET_ROBOT_PERCENTAGE / 100))
            if robots_in_target >= required_robots:
                if not self.target_found:
                    self.target_found = True
                    self.target_found_iteration = self.iteration
                    print(f"\n✓ CONDITION MET: {TARGET_ROBOT_PERCENTAGE}% of robots ({robots_in_target}/{total_robots}) reached target!")
    
    def _count_robots_near_target(self, radius: float = 10.0) -> int:
        """Count robots within specified radius of target."""
        count = 0
        for robot in self.robots:
            if self.environment.distance_to_target(robot.x, robot.y) <= radius:
                count += 1
        return count
    
    def _get_avg_robot_speed(self) -> float:
        """Get average speed of all robots."""
        speeds = [np.sqrt(r.vx**2 + r.vy**2) for r in self.robots]
        return np.mean(speeds) if speeds else 0.0
    
    def get_robot_positions(self) -> List[tuple]:
        """Get current positions of all robots."""
        return [(r.x, r.y) for r in self.robots]
    
    def get_robot_velocities(self) -> List[tuple]:
        """Get current velocities of all robots."""
        return [(r.vx, r.vy) for r in self.robots]
    
    def get_swarm_center(self) -> tuple:
        """Get center of mass of swarm."""
        if not self.robots:
            return 0, 0
        center_x = np.mean([r.x for r in self.robots])
        center_y = np.mean([r.y for r in self.robots])
        return center_x, center_y
    
    def get_swarm_spread(self) -> float:
        """Get average distance of robots from swarm center."""
        if not self.robots:
            return 0.0
        center_x, center_y = self.get_swarm_center()
        distances = [np.sqrt((r.x - center_x)**2 + (r.y - center_y)**2) 
                    for r in self.robots]
        return np.mean(distances)
    
    def reset(self):
        """Reset swarm for new simulation."""
        self.robots = self._create_robots()
        self.pso = PSO(self.num_robots)
        self.iteration = 0
        self.target_found = False
        self.target_found_iteration = None
        self.environment.visited_regions.clear()

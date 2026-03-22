"""
Particle Swarm Optimization (PSO) algorithm implementation.
Adapted for swarm robotic path planning and exploration.
"""

import numpy as np
from typing import List, Tuple, Callable


class PSO:
    """
    Particle Swarm Optimization algorithm for path planning and exploration.
    """
    
    def __init__(self, num_particles: int, 
                 w: float = 0.7298,
                 c1: float = 1.49618,
                 c2: float = 1.49618):
        """
        Initialize PSO algorithm.
        
        Args:
            num_particles: Number of particles (robots)
            w: Inertia weight
            c1: Cognitive parameter
            c2: Social parameter
        """
        self.num_particles = num_particles
        self.w = w
        self.c1 = c1
        self.c2 = c2
        
        self.global_best_x = None
        self.global_best_y = None
        self.global_best_fitness = float('-inf')
        
        self.fitness_history = []
        self.iteration = 0
    
    def fitness_function(self, robots, environment, 
                        target_weight: float = 1.0,
                        exploration_weight: float = 0.3) -> List[float]:
        """
        Compute fitness values for all robots.
        
        The fitness is based on:
        1. Distance to target (closer is better)
        2. Exploration (being in unexplored areas is better)
        3. Obstacle avoidance (staying away from obstacles)
        
        Args:
            robots: List of Robot objects
            environment: Environment object
            target_weight: Weight for target distance objective
            exploration_weight: Weight for exploration objective
            
        Returns:
            List of fitness values for each robot
        """
        fitness_values = []
        
        for robot in robots:
            # Target distance cost (negative = want to minimize)
            dist_to_target = environment.distance_to_target(robot.x, robot.y)
            target_fitness = -target_weight * dist_to_target
            
            # Exploration bonus - reward visiting new areas
            exploration_fitness = 0.0
            nearby_obstacles = environment.get_obstacles_in_range(
                robot.x, robot.y, robot.sensor_range
            )
            if nearby_obstacles:
                # Reward exploring near obstacles (more challenging environment)
                exploration_fitness = exploration_weight * len(nearby_obstacles)
            
            # Obstacle avoidance - penalize being too close
            min_obstacle_dist = float('inf')
            if nearby_obstacles:
                for obs in nearby_obstacles:
                    obs_dist = obs.distance_to_point(robot.x, robot.y)
                    min_obstacle_dist = min(min_obstacle_dist, obs_dist)
            
            # Fitness combines targets and exploration
            fitness = target_fitness + exploration_fitness
            
            # Penalize very close proximity to obstacles
            if min_obstacle_dist < 5.0:
                fitness -= (5.0 - min_obstacle_dist) * 10
            
            fitness_values.append(fitness)
            
            # Update robot's best position
            robot.update_best_position(fitness)
        
        return fitness_values
    
    def update_global_best(self, robots, fitness_values: List[float]):
        """
        Update global best position based on current fitness.
        
        Args:
            robots: List of Robot objects
            fitness_values: List of fitness values
        """
        best_idx = np.argmax(fitness_values)
        best_fitness = fitness_values[best_idx]
        
        if best_fitness > self.global_best_fitness:
            self.global_best_fitness = best_fitness
            self.global_best_x = robots[best_idx].best_x
            self.global_best_y = robots[best_idx].best_y
        
        self.fitness_history.append(self.global_best_fitness)
    
    def update_swarm(self, robots, environment, 
                    min_obstacle_distance: float = 5.0) -> bool:
        """
        Perform one iteration of PSO algorithm (velocity updates only).
        Position updates and collision handling are done in RobotSwarm.step()
        
        Args:
            robots: List of Robot objects
            environment: Environment object
            min_obstacle_distance: Minimum safe distance from obstacles
            
        Returns:
            True if target was reached by any robot
        """
        # Compute fitness
        fitness_values = self.fitness_function(robots, environment)
        
        # Update global best
        self.update_global_best(robots, fitness_values)
        
        # Update each particle (robot) velocity only
        # Position update and collision handling is done in RobotSwarm.step()
        for robot in robots:
            # Update velocity using PSO rule
            robot.update_velocity(
                robot.best_x, robot.best_y,
                self.global_best_x, self.global_best_y,
                self.w, self.c1, self.c2
            )
        
        # Check if any robot reached target
        target_reached = any(
            environment.is_reached_target(r.x, r.y) for r in robots
        )
        
        self.iteration += 1
        return target_reached
    
    def get_global_best(self) -> Tuple[float, float]:
        """Get global best position found."""
        return self.global_best_x, self.global_best_y
    
    def get_convergence_metrics(self) -> dict:
        """Get PSO convergence metrics."""
        if not self.fitness_history:
            return {}
        
        return {
            'best_fitness': self.global_best_fitness,
            'avg_fitness': np.mean(self.fitness_history),
            'final_fitness': self.fitness_history[-1],
            'iterations': self.iteration
        }

"""
Dynamic Window Approach (DWA) - Local Trajectory Planning.

This module implements DWA for local navigation refinement.
PSO computes global goal direction, DWA refines velocities to avoid obstacles.

Algorithm:
  1. Sample velocity candidates within dynamic window (achievable velocities)
  2. For each candidate velocity, simulate trajectory N steps ahead
  3. Evaluate each trajectory for:
     - Distance to goal (PSO direction)
     - Distance to obstacles (static + dynamic)
     - Heading smoothness (prefer small direction changes)
     - Exploration diversity (sample variance)
  4. Select velocity with best score
  5. Apply heading smoothness filter to reduce jitter

Created: March 29, 2026
Version: 1.0 (Phase 3 - Navigation Intelligence)
"""

import numpy as np
from config.realism_settings import (
    DWA_PREDICTION_STEPS,
    DWA_VELOCITY_SAMPLES,
    DWA_ANGULAR_STEP,
    DWA_LINEAR_STEP,
    DWA_MIN_VELOCITY,
    DWA_MAX_VELOCITY,
    GOAL_WEIGHT,
    OBSTACLE_WEIGHT,
    SMOOTHNESS_WEIGHT,
    EXPLORATION_WEIGHT,
    DWA_COLLISION_DISTANCE,
    DWA_ROBOT_COLLISION_DISTANCE,
    DWA_SAFETY_MARGIN,
    DWA_HEADING_HISTORY,
    DWA_MAX_ANGULAR_VELOCITY,
    ROBOT_RADIUS,
    DEBUG_PHASE3,
    ENABLE_PHASE4_ENVIRONMENT,
    PREDICT_DYNAMIC_COLLISIONS,
    DYNAMIC_COLLISION_SAFETY_MARGIN,
)


class DWAPlanner:
    """
    Dynamic Window Approach planner for local trajectory optimization.
    
    Takes PSO-desired velocity and refines it to avoid obstacles while
    preferring smooth heading changes.
    """
    
    def __init__(self):
        """Initialize DWA planner."""
        self.last_vx = 0.0  # Last selected velocity for smoothness
        self.last_vy = 0.0
        self.last_heading = 0.0
    
    def plan(self, robot_pos, robot_vel, pso_goal_dir, environment, nearby_robots):
        """
        Compute refined velocity using DWA.
        
        Args:
            robot_pos: Tuple (x, y) - current robot position
            robot_vel: Tuple (vx, vy) - current velocity
            pso_goal_dir: Tuple (gx, gy) - PSO desired direction (normalized)
            environment: Environment object with obstacles
            nearby_robots: List of (x, y, vx, vy) for robots in range
            
        Returns:
            Tuple (refined_vx, refined_vy) - velocity after DWA refinement
        """
        # Generate velocity candidates
        velocity_candidates = self._sample_velocities()
        
        # Evaluate each candidate trajectory
        best_score = -np.inf
        best_velocity = (self.last_vx, self.last_vy)
        
        for vx, vy in velocity_candidates:
            # Simulate trajectory
            trajectory = self._simulate_trajectory(robot_pos, (vx, vy))
            
            # Evaluate trajectory
            score = self._evaluate_trajectory(
                trajectory,
                environment,
                robot_pos,
                nearby_robots,
                pso_goal_dir,
                (vx, vy)
            )
            
            if score > best_score:
                best_score = score
                best_velocity = (vx, vy)
        
        # Apply heading smoothness
        refined_vx, refined_vy = self._apply_heading_smoothness(
            best_velocity[0], best_velocity[1]
        )
        
        # Store for next iteration
        self.last_vx = refined_vx
        self.last_vy = refined_vy
        self.last_heading = np.arctan2(refined_vy, refined_vx)
        
        if DEBUG_PHASE3:
            print(f"  DWA: PSO goal={pso_goal_dir}, Refined v=({refined_vx:.2f}, {refined_vy:.2f}), Score={best_score:.2f}")
        
        return refined_vx, refined_vy
    
    def _sample_velocities(self):
        """Generate velocity candidates in dynamic window."""
        candidates = []
        
        # Create circular sample pattern
        for i in range(DWA_VELOCITY_SAMPLES):
            angle = 2 * np.pi * i / DWA_VELOCITY_SAMPLES
            
            # Vary linear speed
            for speed_factor in [0.3, 0.65, 1.0]:
                linear_speed = DWA_MIN_VELOCITY + (DWA_MAX_VELOCITY - DWA_MIN_VELOCITY) * speed_factor
                
                vx = linear_speed * np.cos(angle)
                vy = linear_speed * np.sin(angle)
                
                # Clamp to max velocity magnitude
                mag = np.sqrt(vx*vx + vy*vy)
                if mag > DWA_MAX_VELOCITY:
                    vx = DWA_MAX_VELOCITY * vx / mag
                    vy = DWA_MAX_VELOCITY * vy / mag
                
                candidates.append((vx, vy))
        
        return candidates
    
    def _simulate_trajectory(self, robot_pos, velocity, steps=None):
        """
        Simulate forward trajectory.
        
        Args:
            robot_pos: (x, y) current position
            velocity: (vx, vy) velocity
            steps: Number of steps (defaults to DWA_PREDICTION_STEPS)
            
        Returns:
            List of (x, y) positions along trajectory
        """
        if steps is None:
            steps = DWA_PREDICTION_STEPS
        
        trajectory = [robot_pos]
        x, y = robot_pos
        vx, vy = velocity
        
        for _ in range(steps):
            x += vx
            y += vy
            trajectory.append((x, y))
        
        return trajectory
    
    def _evaluate_trajectory(self, trajectory, environment, start_pos, 
                             nearby_robots, pso_goal_dir, velocity):
        """
        Score trajectory based on multiple objectives.
        
        Returns:
            Score (higher is better)
        """
        score = 0.0
        trajectory_valid = True
        
        # 1. Check trajectory for collisions (early termination)
        for pos in trajectory[1:]:  # Skip first (current position)
            # Check obstacle collision
            for obstacle in environment.obstacles:
                dist = np.sqrt((pos[0] - obstacle.x)**2 + (pos[1] - obstacle.y)**2)
                if dist < obstacle.radius + ROBOT_RADIUS + DWA_SAFETY_MARGIN:
                    trajectory_valid = False
                    break
            
            # Check robot collision
            if trajectory_valid:
                for rx, ry, _, _ in nearby_robots:
                    dist = np.sqrt((pos[0] - rx)**2 + (pos[1] - ry)**2)
                    if dist < 2 * ROBOT_RADIUS + DWA_SAFETY_MARGIN:
                        trajectory_valid = False
                        break
            
            if not trajectory_valid:
                break
        
        # Phase 4: Check dynamic obstacles
        if trajectory_valid and ENABLE_PHASE4_ENVIRONMENT:
            if not self._check_dynamic_obstacles(trajectory, environment):
                trajectory_valid = False
        
        if not trajectory_valid:
            return -1000.0  # Penalize collision trajectories heavily
        
        # 2. Goal alignment (maximize movement toward PSO goal direction)
        end_pos = trajectory[-1]
        move_vec = (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
        move_mag = np.sqrt(move_vec[0]**2 + move_vec[1]**2)
        
        if move_mag > 0.01:
            # Dot product between movement and goal direction
            dot = move_vec[0] * pso_goal_dir[0] + move_vec[1] * pso_goal_dir[1]
            goal_score = dot / (move_mag + 0.01)
        else:
            goal_score = 0.0
        
        score += GOAL_WEIGHT * goal_score
        
        # 3. Safety distance (maximize distance to nearest obstacle/robot)
        min_obstacle_dist = np.inf
        for pos in trajectory[1:]:
            for obstacle in environment.obstacles:
                dist = np.sqrt((pos[0] - obstacle.x)**2 + (pos[1] - obstacle.y)**2)
                dist -= obstacle.radius + ROBOT_RADIUS
                min_obstacle_dist = min(min_obstacle_dist, dist)
            
            for rx, ry, _, _ in nearby_robots:
                dist = np.sqrt((pos[0] - rx)**2 + (pos[1] - ry)**2)
                dist -= 2 * ROBOT_RADIUS
                min_obstacle_dist = min(min_obstacle_dist, dist)
        
        if min_obstacle_dist < np.inf:
            safety_score = max(0, min(DWA_COLLISION_DISTANCE, min_obstacle_dist))
        else:
            safety_score = DWA_COLLISION_DISTANCE
        
        score += OBSTACLE_WEIGHT * safety_score
        
        # 4. Heading smoothness (prefer small angle changes)
        vx, vy = velocity
        heading = np.arctan2(vy, vx)
        angle_change = abs(self._angle_diff(heading, self.last_heading))
        smoothness_score = 1.0 - (angle_change / np.pi)
        
        score += SMOOTHNESS_WEIGHT * smoothness_score
        
        # 5. Exploration variance (prefer diversity in velocity sampling)
        vel_mag = np.sqrt(vx*vx + vy*vy)
        exploration_score = vel_mag / DWA_MAX_VELOCITY if DWA_MAX_VELOCITY > 0 else 0
        
        score += EXPLORATION_WEIGHT * exploration_score
        
        # Phase 4: Terrain cost (penalize slow terrain)
        if ENABLE_PHASE4_ENVIRONMENT:
            terrain_cost = self._evaluate_terrain_cost(trajectory, environment)
            # Penalize trajectories through slow terrain
            score -= terrain_cost * 0.1  # Small penalty to avoid over-weighting
        
        return score
    
    def _apply_heading_smoothness(self, vx, vy):
        """
        Blend heading with previous frame to reduce jitter.
        
        Args:
            vx, vy: Desired velocity (from DWA)
            
        Returns:
            (smoothed_vx, smoothed_vy)
        """
        if DWA_HEADING_HISTORY <= 0:
            return vx, vy
        
        # Blend with previous velocity
        blended_vx = DWA_HEADING_HISTORY * self.last_vx + (1 - DWA_HEADING_HISTORY) * vx
        blended_vy = DWA_HEADING_HISTORY * self.last_vy + (1 - DWA_HEADING_HISTORY) * vy
        
        # Limit angular velocity change
        prev_heading = np.arctan2(self.last_vy, self.last_vx)
        new_heading = np.arctan2(blended_vy, blended_vx)
        angle_change = self._angle_diff(new_heading, prev_heading)
        
        if abs(angle_change) > DWA_MAX_ANGULAR_VELOCITY:
            # Clamp angle change
            clamped_angle = prev_heading + np.clip(
                angle_change, 
                -DWA_MAX_ANGULAR_VELOCITY, 
                DWA_MAX_ANGULAR_VELOCITY
            )
            mag = np.sqrt(blended_vx**2 + blended_vy**2)
            blended_vx = mag * np.cos(clamped_angle)
            blended_vy = mag * np.sin(clamped_angle)
        
        return blended_vx, blended_vy
    
    def _angle_diff(self, angle1, angle2):
        """Compute smallest angle difference (handles wraparound)."""
        diff = angle1 - angle2
        while diff > np.pi:
            diff -= 2 * np.pi
        while diff < -np.pi:
            diff += 2 * np.pi
        return diff
    
    # ========== PHASE 4: Environment Complexity ==========
    
    def _check_dynamic_obstacles(self, trajectory, environment):
        """
        Check trajectory against dynamic obstacles (Phase 4).
        
        Args:
            trajectory: List of positions to check
            environment: Environment with dynamic obstacles
            
        Returns:
            True if trajectory is collision-free
        """
        if not ENABLE_PHASE4_ENVIRONMENT:
            return True
        
        if not environment.dynamic_obstacles or not environment.dynamic_obstacles.obstacles:
            return True
        
        for pos in trajectory[1:]:
            for obs in environment.dynamic_obstacles.obstacles:
                # Check against predicted obstacle position
                predicted_pos = obs.predict_position(len(trajectory))
                dist = np.sqrt((pos[0] - predicted_pos[0])**2 + (pos[1] - predicted_pos[1])**2)
                
                if dist < obs.radius + ROBOT_RADIUS + DYNAMIC_COLLISION_SAFETY_MARGIN:
                    return False
        
        return True
    
    def _evaluate_terrain_cost(self, trajectory, environment):
        """
        Evaluate trajectory cost based on terrain (Phase 4).
        
        Terrain may slow movement or introduce randomness. Account for this
        in trajectory evaluation.
        
        Args:
            trajectory: List of positions
            environment: Environment with terrain system
            
        Returns:
            Terrain-based cost multiplier (>1 for unfavorable terrain)
        """
        if not ENABLE_PHASE4_ENVIRONMENT:
            return 1.0
        
        if not environment.terrain_system:
            return 1.0
        
        total_cost = 0.0
        for pos in trajectory[1:]:
            speed_mult = environment.terrain_system.get_speed_multiplier(pos[0], pos[1])
            # Cost is inverse of speed multiplier (slow terrain = high cost)
            terrain_cost = 1.0 / max(speed_mult, 0.1)
            total_cost += terrain_cost
        
        # Average cost over trajectory
        return total_cost / max(len(trajectory) - 1, 1)


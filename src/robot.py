"""
Robot agent module for swarm robotics simulation.
Represents individual differential-drive ground robots.
Implements realistic differential steering kinematics.

Phase 1 Physics (v3.0):
- Battery/energy management system
- Motor acceleration smoothing
- Motor response delay queue
"""

import numpy as np
from typing import Tuple
from collections import deque


class DifferentialDriveRobot:
    """
    Represents a differential-drive ground robot (like wheeled robots).
    
    Motion model:
    - Two independent wheels (left and right)
    - Forward/backward motion: average of wheel velocities
    - Rotation: difference between wheel velocities
    - Realistic kinematics with heading/orientation
    """
    
    def __init__(self, robot_id: int, x: float, y: float, 
                 max_speed: float = 2.0, sensor_range: float = 15.0,
                 wheel_distance: float = 2.0):
        """
        Initialize a differential-drive robot.
        
        Args:
            robot_id: Unique robot identifier
            x: Initial x position
            y: Initial y position
            max_speed: Maximum wheel velocity
            sensor_range: Sensing range for environment detection
            wheel_distance: Distance between wheels (wheelbase) - affects turning radius
        """
        self.id = robot_id
        
        # Position and orientation
        self.x = x
        self.y = y
        self.theta = np.random.uniform(0, 2 * np.pi)  # Heading angle (radians)
        
        # Wheel velocities (instead of vx, vy)
        self.v_left = 0.0   # Left wheel velocity (actual)
        self.v_right = 0.0  # Right wheel velocity (actual)
        self.max_speed = max_speed
        
        # Robot parameters
        self.wheel_distance = wheel_distance  # Distance between wheels (wheelbase)
        self.sensor_range = sensor_range
        
        # Best position discovered by this robot
        self.best_x = x
        self.best_y = y
        self.best_fitness = float('-inf')
        
        # Desired movement direction (for PSO)
        self.desired_heading = self.theta
        self.desired_speed = 0.0
        
        # ===== PHASE 1: Core Physics =====
        # Battery/Energy system
        self.battery = 100.0  # Current battery (0-100%)
        self.battery_capacity = 100.0
        self.home_location = (0, 0)
        
        # Motor acceleration smoothing
        self.v_left_target = 0.0   # Target velocities from PSO
        self.v_right_target = 0.0
        
        # Motor response delay queue
        self.command_delay = 2  # Frames of latency
        self.v_left_queue = deque(maxlen=2)   # Command queue
        self.v_right_queue = deque(maxlen=2)
    
    def update_velocity(self, best_x: float, best_y: float, 
                       global_best_x: float, global_best_y: float,
                       w: float = 0.7298, c1: float = 1.49618, 
                       c2: float = 1.49618):
        """
        Update velocity using PSO update rule adapted for differential steering.
        
        PSO computes desired velocity as (vx, vy) which we convert to wheel commands.
        Phase 1: Respects battery constraints (won't move if dead).
        
        Args:
            best_x: Robot's best position x
            best_y: Robot's best position y
            global_best_x: Swarm's global best position x
            global_best_y: Swarm's global best position y
            w: Inertia weight
            c1: Cognitive parameter
            c2: Social parameter
        """
        # Check battery - if dead, can't move
        if self.battery <= 0:
            self.desired_speed = 0
            self._velocity_to_wheels()
            return
        
        r1 = np.random.uniform(0, 1)
        r2 = np.random.uniform(0, 1)
        
        # Compute desired velocity components (as in omnidirectional PSO)
        vx = (w * self.desired_speed * np.cos(self.desired_heading) + 
              c1 * r1 * (best_x - self.x) + 
              c2 * r2 * (global_best_x - self.x))
        
        vy = (w * self.desired_speed * np.sin(self.desired_heading) + 
              c1 * r1 * (best_y - self.y) + 
              c2 * r2 * (global_best_y - self.y))
        
        # Convert desired velocity (vx, vy) to heading and speed
        desired_speed = np.sqrt(vx**2 + vy**2)
        if desired_speed > 0.01:  # Only update if there's meaningful movement
            self.desired_heading = np.arctan2(vy, vx)
        
        # Limit speed
        if desired_speed > self.max_speed:
            desired_speed = self.max_speed
        
        # Phase 1: Battery constraint - reduce speed if low on battery
        if self.battery < 20:  # BATTERY_LOW_THRESHOLD
            desired_speed *= (self.battery / 100.0)
        
        self.desired_speed = desired_speed
        
        # Convert desired motion to wheel velocities
        self._velocity_to_wheels()
    
    def _velocity_to_wheels(self):
        """
        Convert desired heading and speed to differential wheel commands.
        
        This uses a simple control law:
        - Forward motion: v = desired_speed
        - Rotation: ω based on difference between desired and current heading
        
        Phase 1: Sets target velocities (will be smoothed by acceleration limiter).
        Phase 1: Queues commands for motor delay system.
        """
        # Desired linear velocity
        v_forward = self.desired_speed
        
        # Angular velocity to align with desired heading
        heading_error = self._normalize_angle(self.desired_heading - self.theta)
        
        # Proportional control for heading (turning)
        # Kp = proportional gain (tune this for desired turning response)
        Kp_heading = 0.5  # Adjust this for stronger/weaker heading correction
        omega = Kp_heading * heading_error
        
        # Limit angular velocity (to prevent unrealistic spinning)
        max_angular_velocity = self.max_speed / (self.wheel_distance / 2)
        omega = np.clip(omega, -max_angular_velocity, max_angular_velocity)
        
        # Convert (v, ω) to wheel velocities using differential drive kinematics
        # v_left = v - (L/2) * ω
        # v_right = v + (L/2) * ω
        # where L is wheel_distance
        
        half_wheelbase = self.wheel_distance / 2
        
        # Phase 1: Compute targets (not direct assignment)
        v_left_target = v_forward - half_wheelbase * omega
        v_right_target = v_forward + half_wheelbase * omega
        
        # Limit individual wheel speeds
        v_left_target = np.clip(v_left_target, -self.max_speed, self.max_speed)
        v_right_target = np.clip(v_right_target, -self.max_speed, self.max_speed)
        
        # Phase 1: Set targets and queue commands for motor delay
        self.v_left_target = v_left_target
        self.v_right_target = v_right_target
        
        # Queue commands for motor response delay
        self.v_left_queue.append(v_left_target)
        self.v_right_queue.append(v_right_target)
    
    def update_position(self):
        """
        Update robot position and heading based on wheel velocities.
        
        Uses differential drive kinematics:
        - Forward velocity: v = (v_left + v_right) / 2
        - Angular velocity: ω = (v_right - v_left) / wheel_distance
        
        Phase 1: Applies motor delay, then acceleration smoothing, then battery drain.
        """
        # Phase 1: Apply motor response delay (if enabled)
        self.apply_motor_delay()
        
        # Phase 1: Apply acceleration smoothing (if enabled)
        self.apply_acceleration_smoothing()
        
        # Compute linear and angular velocities from wheel commands
        v_linear = (self.v_left + self.v_right) / 2.0
        omega = (self.v_right - self.v_left) / self.wheel_distance
        
        # Update position and heading
        if abs(omega) < 0.001:  # Going straight (or nearly straight)
            # Simple forward motion
            self.x += v_linear * np.cos(self.theta)
            self.y += v_linear * np.sin(self.theta)
        else:
            # Turning motion (using differential drive kinematics)
            radius = v_linear / omega if abs(omega) > 0.0001 else float('inf')
            self.theta += omega
            self.theta = self._normalize_angle(self.theta)
            
            self.x += radius * (np.sin(self.theta) - np.sin(self.theta - omega))
            self.y += radius * (-np.cos(self.theta) + np.cos(self.theta - omega))
        
        # Phase 1: Update battery based on speed (must be after position update)
        self.update_battery()
    
    @staticmethod
    def _normalize_angle(angle: float) -> float:
        """Normalize angle to [-π, π]."""
        while angle > np.pi:
            angle -= 2 * np.pi
        while angle < -np.pi:
            angle += 2 * np.pi
        return angle
    
    def enforce_bounds(self, width: float, height: float, boundary_margin: float = 1.0):
        """
        Enforce environment boundaries and bounce if out of bounds.
        
        Args:
            width: Environment width
            height: Environment height
            boundary_margin: Margin from boundary
        """
        bounced = False
        
        if self.x < boundary_margin:
            self.x = boundary_margin
            self.theta = self._normalize_angle(np.pi - self.theta)  # Reflect heading
            bounced = True
        elif self.x > width - boundary_margin:
            self.x = width - boundary_margin
            self.theta = self._normalize_angle(np.pi - self.theta)  # Reflect heading
            bounced = True
        
        if self.y < boundary_margin:
            self.y = boundary_margin
            self.theta = self._normalize_angle(-self.theta)  # Reflect heading
            bounced = True
        elif self.y > height - boundary_margin:
            self.y = height - boundary_margin
            self.theta = self._normalize_angle(-self.theta)  # Reflect heading
            bounced = True
        
        # Dampen velocity after bounce
        if bounced:
            self.v_left *= 0.3
            self.v_right *= 0.3
    
    def avoid_obstacle(self, obstacle_x: float, obstacle_y: float, 
                      obstacle_radius: float, min_safe_distance: float = 5.0):
        """
        Adjust desired heading to avoid obstacle with repulsion.
        
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
            
            # Calculate repulsion heading
            repulsion_heading = np.arctan2(dy, dx)
            
            # Blend repulsion with desired heading
            self.desired_heading = (repulsion_heading * 0.7 + 
                                   self.desired_heading * 0.3)
            self.desired_heading = self._normalize_angle(self.desired_heading)
    
    def predict_collision(self, obstacles: list, safety_radius: float = 2.0) -> bool:
        """
        Predict if the next move will result in collision.
        
        Args:
            obstacles: List of Obstacle objects
            safety_radius: Safety buffer
            
        Returns:
            True if collision predicted
        """
        v_linear = (self.v_left + self.v_right) / 2.0
        next_x = self.x + v_linear * np.cos(self.theta)
        next_y = self.y + v_linear * np.sin(self.theta)
        
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
                if dist_to_obs < 0.1:
                    dist_to_obs = 0.1
                
                dx = self.x - obs.x
                dy = self.y - obs.y
                
                # Push robot outside obstacle
                push_distance = obs.radius + 2.0
                self.x = obs.x + (dx / dist_to_obs) * push_distance
                self.y = obs.y + (dy / dist_to_obs) * push_distance
                
                # Reflect heading away from obstacle and reverse velocities
                escape_heading = np.arctan2(dy, dx)
                self.theta = escape_heading
                self.desired_heading = escape_heading
                
                # Reverse and dampen wheel velocities (bounce effect)
                self.v_left *= -0.5
                self.v_right *= -0.5
    
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
        pass  # Not used in differential drive model
    
    def get_position(self) -> Tuple[float, float]:
        """Get current position."""
        return self.x, self.y
    
    def get_heading(self) -> float:
        """Get current heading (orientation) in radians."""
        return self.theta
    
    def get_wheel_velocities(self) -> Tuple[float, float]:
        """Get current wheel velocities (left, right)."""
        return self.v_left, self.v_right
    
    def get_linear_velocity(self) -> float:
        """Get forward linear velocity."""
        return (self.v_left + self.v_right) / 2.0
    
    def get_angular_velocity(self) -> float:
        """Get angular velocity (rotation)."""
        return (self.v_right - self.v_left) / self.wheel_distance
    
    def distance_to(self, x: float, y: float) -> float:
        """Calculate distance to a point."""
        return np.sqrt((self.x - x)**2 + (self.y - y)**2)
    
    def get_orientation_vector(self, scale: float = 1.0) -> Tuple[float, float]:
        """
        Get unit vector in direction robot is heading.
        
        Args:
            scale: Scale factor for visualization
            
        Returns:
            (dx, dy) components of heading vector
        """
        return scale * np.cos(self.theta), scale * np.sin(self.theta)
    
    # ===== PHASE 1: Core Physics Methods =====
    
    def apply_motor_delay(self):
        """
        Apply motor response delay by reading from command queue.
        
        Commands are queued in _velocity_to_wheels() and applied here with delay.
        This simulates latency in motor response (USB lag, onboard processing, etc.).
        """
        # If queue has commands, pop the oldest one
        if self.v_left_queue:
            delayed_v_left = self.v_left_queue.popleft()
            self.v_left = delayed_v_left
        
        if self.v_right_queue:
            delayed_v_right = self.v_right_queue.popleft()
            self.v_right = delayed_v_right
    
    def apply_acceleration_smoothing(self):
        """
        Smooth velocity transitions towards target velocities.
        
        Real motors can't change speed instantly. This ramps actual velocity
        towards target velocity at a limited acceleration rate, creating
        smooth, realistic motion trajectories.
        """
        max_delta = 0.5  # MAX_ACCELERATION from realism_settings
        
        # Smooth left wheel velocity
        if self.v_left < self.v_left_target:
            self.v_left = min(self.v_left + max_delta, self.v_left_target)
        elif self.v_left > self.v_left_target:
            self.v_left = max(self.v_left - max_delta, self.v_left_target)
        
        # Smooth right wheel velocity
        if self.v_right < self.v_right_target:
            self.v_right = min(self.v_right + max_delta, self.v_right_target)
        elif self.v_right > self.v_right_target:
            self.v_right = max(self.v_right - max_delta, self.v_right_target)
    
    def update_battery(self):
        """
        Update battery level based on current wheel velocities.
        
        Physics model:
        - Idle drain: constant small power draw
        - Speed drain: proportional to (v_left^2 + v_right^2)
        - High speeds cost exponentially more energy (quadratic relationship)
        - Recharging at home base (0, 0)
        
        This creates emergent behavior where PSO learns energy-efficient paths.
        """
        # Calculate instantaneous power consumption
        base_drain = 0.05          # BATTERY_DRAIN_RATE
        speed_penalty = 0.015      # BATTERY_SPEED_PENALTY
        
        speed_squared = self.v_left**2 + self.v_right**2
        drain = base_drain + speed_penalty * speed_squared
        
        # Check if robot is at home location (charging)
        dist_to_home = np.sqrt(self.x**2 + self.y**2)
        recharge_distance = 3.0  # BATTERY_RECHARGE_DISTANCE
        
        if dist_to_home < recharge_distance:
            # Charging mode: recharge faster than drain
            recharge_rate = 2.0  # BATTERY_RECHARGE_RATE
            self.battery = min(100.0, self.battery + recharge_rate)
        else:
            # Normal operation: drain battery
            self.battery = max(0, self.battery - drain)
    
    def get_battery_status(self) -> dict:
        """
        Get current battery status information.
        
        Returns:
            Dictionary with battery statistics
        """
        return {
            'battery_percent': self.battery,
            'is_charging': np.sqrt(self.x**2 + self.y**2) < 3.0,
            'energy_drain_rate': 0.05 + 0.015 * (self.v_left**2 + self.v_right**2),
            'distance_to_home': np.sqrt(self.x**2 + self.y**2)
        }
    
    @property
    def vx(self) -> float:
        """Get x-component of velocity (for backward compatibility)."""
        v_linear = self.get_linear_velocity()
        return v_linear * np.cos(self.theta)
    
    @property
    def vy(self) -> float:
        """Get y-component of velocity (for backward compatibility)."""
        v_linear = self.get_linear_velocity()
        return v_linear * np.sin(self.theta)


# Keep original Robot class for backward compatibility
class Robot(DifferentialDriveRobot):
    """Alias for DifferentialDriveRobot for backward compatibility."""
    pass

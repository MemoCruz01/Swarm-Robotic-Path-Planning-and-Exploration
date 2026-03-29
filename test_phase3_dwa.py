"""
Phase 3 Test Suite - Navigation Intelligence with DWA

Tests for Dynamic Window Approach (DWA) local trajectory planning.
Verifies that DWA successfully:
  - Samples velocity candidates in dynamic window
  - Predicts trajectories without collisions
  - Balances goal alignment with obstacle avoidance
  - Applies heading smoothness filtering
  - Integrates with PSO refinement layer

Run: python -m pytest test_phase3_dwa.py -v
"""

import pytest
import numpy as np
from src.dwa_planner import DWAPlanner
from src.environment import Environment, Obstacle
from src.robot import DifferentialDriveRobot


class TestDWAPlanner:
    """Tests for DWA planner core functionality."""
    
    @pytest.fixture
    def dwa_planner(self):
        """Create a fresh DWA planner for each test."""
        return DWAPlanner()
    
    @pytest.fixture
    def simple_env(self):
        """Create simple test environment."""
        env = Environment(100, 100)
        # Add a few obstacles
        env.obstacles = [
            Obstacle(x=30, y=50, radius=5),
            Obstacle(x=70, y=50, radius=5),
        ]
        env.target_x = 80
        env.target_y = 80
        return env
    
    def test_dwa_velocity_sampling(self, dwa_planner):
        """Test DWA generates velocity candidates."""
        from config.realism_settings import DWA_VELOCITY_SAMPLES
        
        # Get candidates multiple times - should be consistent pattern
        candidates1 = dwa_planner._sample_velocities()
        candidates2 = dwa_planner._sample_velocities()
        
        # Should have multiple candidates
        assert len(candidates1) > DWA_VELOCITY_SAMPLES
        assert len(candidates2) > DWA_VELOCITY_SAMPLES
        
        # Each velocity should be valid (not NaN, reasonable magnitude)
        for vx, vy in candidates1:
            assert not np.isnan(vx) and not np.isnan(vy)
            assert abs(vx) <= 2.0  # Reasonable speed
            assert abs(vy) <= 2.0
    
    def test_dwa_trajectory_simulation(self, dwa_planner):
        """Test DWA simulates trajectories correctly."""
        from config.realism_settings import DWA_PREDICTION_STEPS
        
        start_pos = (50, 50)
        velocity = (0.5, 0.3)
        
        trajectory = dwa_planner._simulate_trajectory(start_pos, velocity)
        
        # Should have START + STEPS positions
        assert len(trajectory) == DWA_PREDICTION_STEPS + 1
        assert trajectory[0] == start_pos
        
        # Final position should be start + velocity * steps
        expected_final_x = start_pos[0] + velocity[0] * DWA_PREDICTION_STEPS
        expected_final_y = start_pos[1] + velocity[1] * DWA_PREDICTION_STEPS
        
        assert abs(trajectory[-1][0] - expected_final_x) < 0.01
        assert abs(trajectory[-1][1] - expected_final_y) < 0.01
    
    def test_dwa_collision_detection(self, dwa_planner, simple_env):
        """Test DWA detects collisions in trajectory."""
        # Trajectory heading toward obstacle at (30, 50)
        start_pos = (10, 50)
        velocity = (2.0, 0.0)  # Moving toward obstacle
        
        trajectory = dwa_planner._simulate_trajectory(start_pos, velocity)
        
        # This trajectory should hit the obstacle at (30, 50) with radius 5
        # Evaluate should return low score
        nearby_robots = []
        pso_goal_dir = (1.0, 0.0)
        
        score = dwa_planner._evaluate_trajectory(
            trajectory,
            simple_env,
            start_pos,
            nearby_robots,
            pso_goal_dir,
            velocity
        )
        
        # Score should be heavily penalized (collision = -1000)
        assert score == -1000.0, f"Expected collision penalty, got score={score}"
    
    def test_dwa_safe_trajectory_scoring(self, dwa_planner, simple_env):
        """Test DWA scores safe trajectories positively."""
        # Safe trajectory in open space
        start_pos = (10, 10)
        velocity = (0.5, 0.1)  # Safe forward motion
        
        trajectory = dwa_planner._simulate_trajectory(start_pos, velocity)
        
        nearby_robots = []
        pso_goal_dir = (1.0, 0.0)  # Goal is forward
        
        score = dwa_planner._evaluate_trajectory(
            trajectory,
            simple_env,
            start_pos,
            nearby_robots,
            pso_goal_dir,
            velocity
        )
        
        # Score should be positive (safe, aligned with goal)
        assert score > 0, f"Expected positive score for safe trajectory, got {score}"
    
    def test_dwa_heading_smoothness(self, dwa_planner):
        """Test DWA smooths heading changes."""
        # Set previous velocity/heading
        dwa_planner.last_vx = 1.0
        dwa_planner.last_vy = 0.0
        dwa_planner.last_heading = 0.0
        
        # Try to apply large sudden heading change
        from config.realism_settings import DWA_HEADING_HISTORY
        
        new_vx = -1.0  # 180 degree turn
        new_vy = 0.0
        
        smoothed_vx, smoothed_vy = dwa_planner._apply_heading_smoothness(new_vx, new_vy)
        
        # Smoothed velocity should be less extreme than requested
        angle_smoothed = np.arctan2(smoothed_vy, smoothed_vx)
        angle_requested = np.arctan2(new_vy, new_vx)
        
        angle_diff = abs(angle_smoothed - dwa_planner.last_heading)
        requested_diff = abs(angle_requested - dwa_planner.last_heading)
        
        # If heading smoothing is enabled, should apply blending
        if DWA_HEADING_HISTORY > 0:
            assert angle_diff <= requested_diff, "Heading should be smoothed"
    
    def test_dwa_angle_diff_wraparound(self, dwa_planner):
        """Test DWA angle difference handles wraparound correctly."""
        # Test cases where angles wrap around pi/-pi
        
        # Small difference
        diff = dwa_planner._angle_diff(0.1, 0.0)
        assert abs(diff - 0.1) < 0.01
        
        # Large positive (should wrap)
        diff = dwa_planner._angle_diff(3.0, -3.0)
        expected = 3.0 - (-3.0)
        while expected > np.pi:
            expected -= 2 * np.pi
        assert abs(diff - expected) < 0.01
        
        # Negative difference
        diff = dwa_planner._angle_diff(0.0, 0.1)
        assert abs(diff - (-0.1)) < 0.01
    
    def test_dwa_plan_method(self, dwa_planner, simple_env):
        """Test DWA plan() integrates all components."""
        robot_pos = (40, 40)
        robot_vel = (0.5, 0.0)
        pso_goal_dir = (1.0, 0.0)
        nearby_robots = []
        
        # Run DWA planning
        refined_vx, refined_vy = dwa_planner.plan(
            robot_pos,
            robot_vel,
            pso_goal_dir,
            simple_env,
            nearby_robots
        )
        
        # Should return valid velocities
        assert not np.isnan(refined_vx) and not np.isnan(refined_vy)
        assert isinstance(refined_vx, (float, np.floating))
        assert isinstance(refined_vy, (float, np.floating))
        
        # Velocity magnitude should be reasonable
        mag = np.sqrt(refined_vx**2 + refined_vy**2)
        assert mag <= 2.0, f"Refined velocity too large: {mag}"
    
    def test_dwa_avoids_obstacles(self, dwa_planner, simple_env):
        """Test DWA avoids obstacles over goal alignment."""
        robot_pos = (25, 50)
        robot_vel = (0.3, 0.0)
        pso_goal_dir = (1.0, 0.0)  # Goal is to RIGHT, but obstacle is there!
        nearby_robots = []
        
        # Obstacle at (30, 50) should force avoidance
        refined_vx, refined_vy = dwa_planner.plan(
            robot_pos,
            robot_vel,
            pso_goal_dir,
            simple_env,
            nearby_robots
        )
        
        # Refined velocity should have significant Y component (circumnavigate)
        # or be very small (don't hit obstacle)
        mag = np.sqrt(refined_vx**2 + refined_vy**2)
        
        # Either small (stopped) or redirected (nonzero Y component)
        if mag > 0.1:
            assert abs(refined_vy) > 0.05, "Should redirect to avoid obstacle"
    
    def test_dwa_multiple_calls(self, dwa_planner, simple_env):
        """Test DWA maintains state across multiple calls."""
        params = {
            'robot_pos': (40, 40),
            'pso_goal_dir': (1.0, 0.0),
            'environment': simple_env,
            'nearby_robots': []
        }
        
        # Call multiple times with same state
        results = []
        for _ in range(3):
            vx, vy = dwa_planner.plan(
                params['robot_pos'],
                (0.5, 0.0),  # Current velocity
                params['pso_goal_dir'],
                params['environment'],
                params['nearby_robots']
            )
            results.append((vx, vy))
        
        # All three calls should complete without error
        assert len(results) == 3
        for vx, vy in results:
            assert not np.isnan(vx) and not np.isnan(vy)


class TestDWAIntegration:
    """Tests for DWA integration with swarm system."""
    
    def test_phase3_configuration(self):
        """Test Phase 3 configuration is properly set."""
        from config.realism_settings import (
            ENABLE_PHASE3_NAVIGATION,
            USE_DWA,
            DWA_PREDICTION_STEPS,
            GOAL_WEIGHT,
            OBSTACLE_WEIGHT,
        )
        
        assert ENABLE_PHASE3_NAVIGATION is True
        assert USE_DWA is True
        assert DWA_PREDICTION_STEPS > 0
        assert GOAL_WEIGHT > 0
        assert OBSTACLE_WEIGHT > 0
    
    def test_dwa_with_robot_model(self):
        """Test DWA works with actual robot from swarm."""
        from src.swarm import RobotSwarm
        
        simple_env = Environment(100, 100)
        simple_env.target_x = 80
        simple_env.target_y = 80
        
        swarm = RobotSwarm(3, simple_env, robot_speed=2.0)
        
        # Swarm should have DWA planners initialized
        assert len(swarm.dwa_planners) == 3
        assert all(isinstance(p, DWAPlanner) for p in swarm.dwa_planners)
    
    def test_dwa_step_execution(self):
        """Test DWA executes during swarm step without errors."""
        from src.swarm import RobotSwarm
        
        simple_env = Environment(100, 100)
        simple_env.target_x = 80
        simple_env.target_y = 80
        
        swarm = RobotSwarm(3, simple_env, robot_speed=2.0)
        
        # Run a few steps - should not crash
        for _ in range(5):
            stats = swarm.step()
            assert 'best_fitness' in stats
            assert not stats['target_found']  # shouldn't reach target in 5 steps


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

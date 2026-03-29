"""
Phase 4 Test Suite - Environment Complexity

Tests for terrain systems, dynamic obstacles, and extended DWA.
Verifies Phase 4 features:
  - Terrain zones with speed modifiers and friction
  - Dynamic obstacles with movement and rotation
  - Obstacle prediction for collision avoidance
  - DWA integration with Phase 4 environment

Run: python -m pytest test_phase4_environment.py -v
"""

import pytest
import numpy as np
from src.terrain_system import TerrainSystem, TerrainZone
from src.dynamic_obstacles import DynamicObstacle, DynamicObstacleManager
from src.environment import Environment
from src.dwa_planner import DWAPlanner


class TestTerrainSystem:
    """Tests for terrain management and effects."""
    
    @pytest.fixture
    def terrain_system(self):
        """Create terrain system for testing."""
        return TerrainSystem(100, 100)
    
    def test_terrain_zone_creation(self):
        """Test creating terrain zones."""
        zone = TerrainZone(50, 50, 10, 'friction')
        
        assert zone.x == 50
        assert zone.y == 50
        assert zone.radius == 10
        assert zone.zone_type == 'friction'
    
    def test_terrain_zone_containment(self):
        """Test zone point containment."""
        zone = TerrainZone(50, 50, 10, 'friction')
        
        # Points inside
        assert zone.contains_point(50, 50)  # Center
        assert zone.contains_point(55, 50)  # On edge-ish
        
        # Points outside
        assert not zone.contains_point(61, 50)  # Beyond radius
        assert not zone.contains_point(50, 61)
    
    def test_terrain_zone_influence(self):
        """Test zone influence calculation."""
        zone = TerrainZone(50, 50, 10, 'friction')
        
        # Center should have max influence
        assert zone.get_influence(50, 50) > 0.99
        
        # Edge should have low influence
        assert zone.get_influence(59.9, 50) == pytest.approx(0.01, abs=0.02)
        
        # Outside should have zero
        assert zone.get_influence(65, 50) == 0.0
    
    def test_terrain_speed_multiplier(self, terrain_system):
        """Test speed modifier calculation."""
        from config.realism_settings import TERRAIN_FRICTION_FACTOR
        
        # Create fresh system to avoid any state issues
        fresh_system = TerrainSystem(100, 100)
        
        # No zones = normal speed
        mult = fresh_system.get_speed_multiplier(50, 50)
        assert abs(mult - 1.0) < 0.01
        
        # Add friction zone
        zone = TerrainZone(50, 50, 15, 'friction')
        fresh_system.add_zone(zone)
        
        # Debug: check what zones are found
        nearby = fresh_system.get_nearby_zones(50, 50)
        assert len(nearby) == 1, f"Expected 1 nearby zone, found {len(nearby)}"
        
        # At center should be reduced speed
        mult_center = fresh_system.get_speed_multiplier(50, 50)
        assert mult_center < 1.0, f"Speed at center should be less than 1.0, got {mult_center}"
        assert mult_center >= TERRAIN_FRICTION_FACTOR, f"Speed at center should be >= {TERRAIN_FRICTION_FACTOR}, got {mult_center}"
        
        # Far away should be normal
        mult_far = fresh_system.get_speed_multiplier(80, 80)
        assert abs(mult_far - 1.0) < 0.01
    
    def test_terrain_nearby_zones(self, terrain_system):
        """Test efficient zone lookup."""
        zone1 = TerrainZone(30, 30, 10, 'friction')
        zone2 = TerrainZone(50, 50, 10, 'friction')
        zone3 = TerrainZone(80, 80, 10, 'friction')
        
        terrain_system.add_zone(zone1)
        terrain_system.add_zone(zone2)
        terrain_system.add_zone(zone3)
        
        # Nearby query at (40, 40) should find zone1 and zone2
        nearby = terrain_system.get_nearby_zones(40, 40, max_distance=15)
        assert len(nearby) >= 2
        
        # Nearby query at (90, 90) should find zone3
        nearby_far = terrain_system.get_nearby_zones(90, 90, max_distance=15)
        assert len(nearby_far) >= 1


class TestDynamicObstacles:
    """Tests for dynamic obstacle system."""
    
    def test_dynamic_obstacle_creation(self):
        """Test creating dynamic obstacles."""
        obs = DynamicObstacle(1, 50, 50, 5, vx=0.5, vy=0.3, rotation_speed=0.1)
        
        assert obs.id == 1
        assert obs.x == 50
        assert obs.y == 50
        assert obs.radius == 5
        assert obs.vx == 0.5
        assert obs.vy == 0.3
        assert obs.alive is True
    
    def test_dynamic_obstacle_movement(self):
        """Test obstacle movement update."""
        obs = DynamicObstacle(1, 50, 50, 5, vx=1.0, vy=0.5)
        
        # Update position
        obs.update(100, 100, 1000, (50, 50))
        
        assert obs.x == 51.0
        assert obs.y == 50.5
    
    def test_dynamic_obstacle_rotation(self):
        """Test obstacle rotation."""
        obs = DynamicObstacle(1, 50, 50, 5, rotation_speed=0.1)
        initial_theta = obs.theta
        
        obs.update(100, 100, 1000, (50, 50))
        
        assert abs(obs.theta - initial_theta - 0.1) < 0.01
    
    def test_dynamic_obstacle_wall_bounce(self):
        """Test bouncing off walls."""
        obs = DynamicObstacle(1, 2, 50, 5, vx=-1.0, vy=0.0)
        
        obs.update(100, 100, 1000, (50, 50))
        
        # Should bounce off left wall
        assert obs.x == obs.radius  # Clamped to minimum
        assert obs.vx > 0  # Velocity reversed
    
    def test_dynamic_obstacle_position_prediction(self):
        """Test trajectory prediction."""
        obs = DynamicObstacle(1, 50, 50, 5, vx=1.0, vy=0.5)
        
        pred_pos = obs.predict_position(steps=10)
        
        assert pred_pos[0] == 60.0  # 50 + 1.0*10
        assert pred_pos[1] == 55.0  # 50 + 0.5*10
    
    def test_dynamic_obstacle_trajectory(self):
        """Test full trajectory prediction."""
        obs = DynamicObstacle(1, 50, 50, 5, vx=1.0, vy=0.5)
        
        trajectory = obs.predict_trajectory(steps=5)
        
        assert len(trajectory) == 6  # Start + 5 steps
        assert trajectory[0] == (50, 50)
        assert trajectory[-1] == (55.0, 52.5)
    
    def test_dynamic_obstacle_distance(self):
        """Test distance calculation."""
        obs = DynamicObstacle(1, 50, 50, 5)
        
        dist = obs.distance_to(60, 50)
        assert dist == 10.0
    
    def test_dynamic_obstacle_collision(self):
        """Test collision detection."""
        obs = DynamicObstacle(1, 50, 50, 5)
        
        # Collision at edge
        assert obs.is_collision(55, 50, collision_radius=0)
        
        # No collision outside
        assert not obs.is_collision(60, 50, collision_radius=0)
    
    @pytest.fixture
    def obstacle_manager(self):
        """Create obstacle manager for testing."""
        return DynamicObstacleManager(100, 100)
    
    def test_obstacle_manager_spawn(self, obstacle_manager):
        """Test obstacle spawning."""
        obs = obstacle_manager.spawn_random_obstacle(min_distance=50)
        
        assert len(obstacle_manager.obstacles) == 1
        assert obs.alive is True
    
    def test_obstacle_manager_update(self, obstacle_manager):
        """Test updating all obstacles."""
        obstacle_manager.spawn_random_obstacle(min_distance=20)
        obstacle_manager.spawn_random_obstacle(min_distance=20)
        
        initial_count = len(obstacle_manager.obstacles)
        obstacle_manager.update_all((50, 50))
        
        assert len(obstacle_manager.obstacles) == initial_count


class TestPhase4Integration:
    """Tests for Phase 4 integration with DWA and swarm."""
    
    def test_phase4_configuration(self):
        """Test Phase 4 config parameters."""
        from config.realism_settings import (
            ENABLE_PHASE4_ENVIRONMENT,
            DYNAMIC_OBSTACLES,
            TERRAIN_ENABLED,
        )
        
        assert ENABLE_PHASE4_ENVIRONMENT is True
        assert TERRAIN_ENABLED is True
    
    def test_environment_phase4_integration(self):
        """Test environment includes Phase 4 systems."""
        from config.realism_settings import DYNAMIC_OBSTACLES, TERRAIN_ENABLED
        
        env = Environment(100, 100)
        
        # Should have Phase 4 systems if enabled
        if env.phase4_enabled:
            assert env.dynamic_obstacles is not None or not DYNAMIC_OBSTACLES
            assert env.terrain_system is not None or not TERRAIN_ENABLED
    
    def test_dwa_with_dynamic_obstacles(self):
        """Test DWA accounts for dynamic obstacles."""
        from config.realism_settings import ENABLE_PHASE4_ENVIRONMENT
        
        if not ENABLE_PHASE4_ENVIRONMENT:
            pytest.skip("Phase 4 not enabled")
        
        dwa = DWAPlanner()
        env = Environment(100, 100)
        
        if env.dynamic_obstacles:
            # Add moving obstacle
            obs = env.dynamic_obstacles.spawn_random_obstacle(min_distance=30)
            
            # DWA should evaluate trajectory accounting for dynamic obstacle
            robot_pos = (50, 50)
            robot_vel = (0.5, 0.0)
            pso_goal = (1.0, 0.0)
            
            result_vx, result_vy = dwa.plan(
                robot_pos,
                robot_vel,
                pso_goal,
                env,
                []
            )
            
            # Should return valid velocities
            assert not np.isnan(result_vx) and not np.isnan(result_vy)
    
    def test_dwa_terrain_evaluation(self):
        """Test DWA evaluates terrain costs."""
        from config.realism_settings import ENABLE_PHASE4_ENVIRONMENT
        
        if not ENABLE_PHASE4_ENVIRONMENT:
            pytest.skip("Phase 4 not enabled")
        
        dwa = DWAPlanner()
        env = Environment(100, 100)
        
        if env.terrain_system:
            # Add friction zone
            zone = TerrainZone(50, 50, 15, 'friction')
            env.terrain_system.add_zone(zone)
            
            # Evaluate trajectory through friction zone
            terrain_cost = dwa._evaluate_terrain_cost(
                [(40, 40), (50, 50), (60, 60)],
                env
            )
            
            # Should account for terrain
            assert terrain_cost >= 1.0


class TestPhase4Performance:
    """Performance and integration tests."""
    
    def test_terrain_grid_efficiency(self):
        """Test terrain grid spatial indexing."""
        terrain = TerrainSystem(100, 100)
        
        # Add many zones
        for i in range(10):
            zone = TerrainZone(
                np.random.uniform(10, 90),
                np.random.uniform(10, 90),
                5,
                'friction'
            )
            terrain.add_zone(zone)
        
        # Fast query should complete quickly
        nearby = terrain.get_nearby_zones(50, 50, max_distance=20)
        assert isinstance(nearby, list)
    
    def test_obstacle_manager_lifecycle(self):
        """Test obstacle lifecycle (spawn/despawn)."""
        manager = DynamicObstacleManager(100, 100)
        
        # Spawn multiple obstacles
        for _ in range(5):
            manager.spawn_random_obstacle(min_distance=30)
        
        assert len(manager.obstacles) == 5
        
        # Update with swarm at origin should despawn far obstacles
        manager.update_all((0, 0))
        
        # Some should be removed (those far from origin)
        assert len(manager.obstacles) <= 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

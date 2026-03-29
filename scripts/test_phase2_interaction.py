"""
Phase 2 Robot Interaction Testing Suite.
Tests robot-robot collisions, communication range, and multi-agent coordination.

Tests performed:
1. Collision detection accuracy
2. Collision response (pushing apart)
3. Velocity reversal on collision
4. Communication range filtering
5. Nearby robots information accuracy
6. Integration with swarm physics
7. No collision when robots far apart
8. Elastic vs inelastic collision behavior
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import *
from config.realism_settings import (
    ENABLE_PHASE2_INTERACTION,
    ROBOT_COLLISIONS_ENABLED,
    ROBOT_RADIUS,
    COLLISION_ELASTICITY,
    COLLISION_SEPARATION_SPEED,
    COMMUNICATION_RANGE_ENABLED,
    COMMUNICATION_RANGE,
)
from src.environment import Environment, Obstacle
from src.robot import Robot
from src.swarm import RobotSwarm


def test_collision_detection():
    """Test 1: Collision detection accuracy."""
    print("\nTEST 1: Collision Detection")
    print("-" * 50)
    
    # Create simple environment
    env = Environment(100, 100, obstacles=[], target_x=80, target_y=80)
    
    # Create two robots very close together
    robot1 = Robot(0, 40.0, 50.0, 2.0, 15.0)
    robot2 = Robot(1, 41.5, 50.0, 2.0, 15.0)  # 1.5 units apart
    robots = [robot1, robot2]
    
    # Run collision detection
    collision_count = env.check_robot_collisions(
        robots,
        robot_radius=ROBOT_RADIUS,
        elasticity=COLLISION_ELASTICITY,
        separation_speed=COLLISION_SEPARATION_SPEED
    )
    
    # Verify collision was detected
    print(f"  Robots distance: 1.5 units")
    print(f"  Collision threshold: {2 * ROBOT_RADIUS} units")
    print(f"  Collisions detected: {collision_count}")
    
    assert collision_count == 1, "Collision should be detected"
    print("  Result: PASSED - Collision detected correctly")
    
    return True


def test_collision_response():
    """Test 2: Collision response (robots pushed apart)."""
    print("\nTEST 2: Collision Response - Pushing Apart")
    print("-" * 50)
    
    env = Environment(100, 100, obstacles=[], target_x=80, target_y=80)
    
    # Create two robots colliding along x-axis
    robot1 = Robot(0, 40.0, 50.0, 2.0, 15.0)
    robot2 = Robot(1, 41.8, 50.0, 2.0, 15.0)  # Just overlapping
    initial_dist = np.sqrt((robot2.x - robot1.x)**2 + (robot2.y - robot1.y)**2)
    
    robots = [robot1, robot2]
    
    # Apply collision resolution
    env.check_robot_collisions(
        robots,
        robot_radius=ROBOT_RADIUS,
        elasticity=COLLISION_ELASTICITY,
        separation_speed=COLLISION_SEPARATION_SPEED
    )
    
    # Check distances after collision
    final_dist = np.sqrt((robot2.x - robot1.x)**2 + (robot2.y - robot1.y)**2)
    
    print(f"  Initial distance: {initial_dist:.2f} units")
    print(f"  Final distance: {final_dist:.2f} units")
    print(f"  Separation: {final_dist - initial_dist:.2f} units")
    
    assert final_dist > initial_dist, "Robots should be pushed apart"
    print("  Result: PASSED - Robots pushed apart successfully")
    
    return True


def test_velocity_reversal():
    """Test 3: Velocity reversal on collision."""
    print("\nTEST 3: Velocity Reversal on Collision")
    print("-" * 50)
    
    env = Environment(100, 100, obstacles=[], target_x=80, target_y=80)
    
    # Create two robots with specific velocities
    robot1 = Robot(0, 40.0, 50.0, 2.0, 15.0)
    robot1.v_left = 1.5
    robot1.v_right = 1.5
    
    robot2 = Robot(1, 41.8, 50.0, 2.0, 15.0)
    robot2.v_left = 1.0
    robot2.v_right = 1.0
    
    initial_v1_left = robot1.v_left
    initial_v2_left = robot2.v_left
    
    robots = [robot1, robot2]
    
    # Apply collision resolution
    env.check_robot_collisions(
        robots,
        robot_radius=ROBOT_RADIUS,
        elasticity=COLLISION_ELASTICITY,
        separation_speed=COLLISION_SEPARATION_SPEED
    )
    
    # Check velocity reversal with elasticity
    expected_v1 = -initial_v1_left * COLLISION_ELASTICITY
    expected_v2 = -initial_v2_left * COLLISION_ELASTICITY
    
    print(f"  Robot 1 initial v_left: {initial_v1_left:.2f}")
    print(f"  Robot 1 final v_left: {robot1.v_left:.2f}")
    print(f"  Expected (with elasticity): {expected_v1:.2f}")
    print(f"  Robot 2 initial v_left: {initial_v2_left:.2f}")
    print(f"  Robot 2 final v_left: {robot2.v_left:.2f}")
    print(f"  Expected (with elasticity): {expected_v2:.2f}")
    
    assert abs(robot1.v_left - expected_v1) < 0.01, "Velocity should be reversed with elasticity"
    assert abs(robot2.v_left - expected_v2) < 0.01, "Velocity should be reversed with elasticity"
    print("  Result: PASSED - Velocities reversed correctly")
    
    return True


def test_no_collision_when_far():
    """Test 4: No collision when robots far apart."""
    print("\nTEST 4: No Collision When Robots Far Apart")
    print("-" * 50)
    
    env = Environment(100, 100, obstacles=[], target_x=80, target_y=80)
    
    # Create two robots far apart
    robot1 = Robot(0, 20.0, 50.0, 2.0, 15.0)
    robot2 = Robot(1, 80.0, 50.0, 2.0, 15.0)  # 60 units apart
    
    initial_dist = np.sqrt((robot2.x - robot1.x)**2 + (robot2.y - robot1.y)**2)
    initial_v1 = robot1.v_left
    initial_v2 = robot2.v_left
    
    robots = [robot1, robot2]
    collision_count = env.check_robot_collisions(
        robots,
        robot_radius=ROBOT_RADIUS,
        elasticity=COLLISION_ELASTICITY,
        separation_speed=COLLISION_SEPARATION_SPEED
    )
    
    final_dist = np.sqrt((robot2.x - robot1.x)**2 + (robot2.y - robot1.y)**2)
    
    print(f"  Distance between robots: {initial_dist:.2f} units")
    print(f"  Collision threshold: {2 * ROBOT_RADIUS} units")
    print(f"  Collisions detected: {collision_count}")
    print(f"  Robot 1 velocity unchanged: {robot1.v_left == initial_v1}")
    
    assert collision_count == 0, "No collision should be detected"
    assert robot1.v_left == initial_v1, "Velocities should not change"
    assert abs(final_dist - initial_dist) < 0.01, "Distance should not change"
    print("  Result: PASSED - No collision, state unchanged")
    
    return True


def test_communication_range():
    """Test 5: Communication range filtering."""
    print("\nTEST 5: Communication Range Filtering")
    print("-" * 50)
    
    env = Environment(100, 100, obstacles=[], target_x=80, target_y=80)
    
    # Create swarm with 5 robots
    swarm = RobotSwarm(5, env, robot_speed=2.0, sensor_range=15.0)
    
    # Position robots at specific distances
    swarm.robots[0].x = 50.0
    swarm.robots[0].y = 50.0
    swarm.robots[1].x = 55.0
    swarm.robots[1].y = 50.0  # 5 units away
    swarm.robots[2].x = 65.0
    swarm.robots[2].y = 50.0  # 15 units away
    swarm.robots[3].x = 75.0
    swarm.robots[3].y = 50.0  # 25 units away
    swarm.robots[4].x = 90.0
    swarm.robots[4].y = 50.0  # 40 units away
    
    # Get nearby robots for robot 0 with comm range 20.0
    nearby = swarm.get_nearby_robots(0, communication_range=20.0)
    nearby_ids = [n['id'] for n in nearby]
    
    print(f"  Robot 0 at (50, 50)")
    print(f"  Communication range: 20.0 units")
    print(f"  Robot 1 at 5 units: in range")
    print(f"  Robot 2 at 15 units: in range")
    print(f"  Robot 3 at 25 units: out of range")
    print(f"  Robot 4 at 40 units: out of range")
    print(f"  Nearby robots found: {nearby_ids}")
    
    assert 1 in nearby_ids, "Robot 1 should be in communication range"
    assert 2 in nearby_ids, "Robot 2 should be in communication range"
    assert 3 not in nearby_ids, "Robot 3 should NOT be in communication range"
    assert 4 not in nearby_ids, "Robot 4 should NOT be in communication range"
    print("  Result: PASSED - Communication range filtering works")
    
    return True


def test_nearby_robots_info():
    """Test 6: Nearby robots information accuracy."""
    print("\nTEST 6: Nearby Robots Information Accuracy")
    print("-" * 50)
    
    env = Environment(100, 100, obstacles=[], target_x=80, target_y=80)
    swarm = RobotSwarm(3, env, robot_speed=2.0, sensor_range=15.0)
    
    swarm.robots[0].x = 50.0
    swarm.robots[0].y = 50.0
    swarm.robots[1].x = 53.0
    swarm.robots[1].y = 54.0
    swarm.robots[2].x = 60.0
    swarm.robots[2].y = 50.0
    
    # Set some attributes for testing
    swarm.robots[1].best_pos_x = 55.0
    swarm.robots[1].best_pos_y = 56.0
    swarm.robots[1].best_fitness = -8.5
    
    # Get nearby robots
    nearby = swarm.get_nearby_robots(0, communication_range=30.0)
    
    print(f"  Robot 0 at (50, 50)")
    print(f"  Found {len(nearby)} nearby robots")
    
    for n in nearby:
        dist = np.sqrt((n['x'] - 50)**2 + (n['y'] - 50)**2)
        print(f"  Robot {n['id']}: position=({n['x']}, {n['y']}), distance={n['distance']:.2f}")
        assert abs(n['distance'] - dist) < 0.01, "Distance calculation should be accurate"
    
    # Check robot 1 info
    robot1_info = [n for n in nearby if n['id'] == 1][0]
    assert robot1_info['best_x'] == 55.0, "Best X should be stored"
    assert robot1_info['best_y'] == 56.0, "Best Y should be stored"
    assert robot1_info['best_fitness'] == -8.5, "Best fitness should be stored"
    
    print("  Result: PASSED - Robot information accurate")
    
    return True


def test_integration_with_swarm():
    """Test 7: Integration with swarm physics."""
    print("\nTEST 7: Integration with Swarm Physics")
    print("-" * 50)
    
    # Create simple environment
    obstacles = []
    np.random.seed(42)
    
    for _ in range(3):
        obstacles.append(Obstacle(
            np.random.uniform(10, 90),
            np.random.uniform(10, 90),
            np.random.uniform(3, 6)
        ))
    
    env = Environment(100, 100, obstacles=obstacles, target_x=80, target_y=80)
    swarm = RobotSwarm(5, env, robot_speed=2.0, sensor_range=15.0)
    
    print(f"  Initial swarm size: {len(swarm.robots)}")
    print(f"  Environment: 100x100 with {len(obstacles)} obstacles")
    
    # Run several steps
    collision_steps = 0
    for step in range(10):
        step_data = swarm.step()
        
        # Check that step completes without error
        assert 'iteration' in step_data, "Step should return statistics"
    
    print(f"  Completed 10 simulation steps without errors")
    print(f"  Final swarm spread: {swarm.get_swarm_spread():.2f} units")
    print("  Result: PASSED - Integration test successful")
    
    return True


def test_elasticity_effect():
    """Test 8: Elastic vs inelastic collision behavior."""
    print("\nTEST 8: Elasticity Effect on Collisions")
    print("-" * 50)
    
    env = Environment(100, 100, obstacles=[], target_x=80, target_y=80)
    
    # Test with inelastic collision (elasticity = 0.0)
    robot1a = Robot(0, 40.0, 50.0, 2.0, 15.0)
    robot1a.v_left = 2.0
    robot2a = Robot(1, 41.9, 50.0, 2.0, 15.0)
    robot2a.v_left = -1.0
    
    env.check_robot_collisions(
        [robot1a, robot2a],
        robot_radius=ROBOT_RADIUS,
        elasticity=0.0,
        separation_speed=COLLISION_SEPARATION_SPEED
    )
    
    # Test with elastic collision (elasticity = 0.7)
    robot1b = Robot(2, 40.0, 50.0, 2.0, 15.0)
    robot1b.v_left = 2.0
    robot2b = Robot(3, 41.9, 50.0, 2.0, 15.0)
    robot2b.v_left = -1.0
    
    env.check_robot_collisions(
        [robot1b, robot2b],
        robot_radius=ROBOT_RADIUS,
        elasticity=0.7,
        separation_speed=COLLISION_SEPARATION_SPEED
    )
    
    print(f"  Inelastic (e=0.0): v_left changed from 2.0 to {robot1a.v_left:.2f}")
    print(f"  Elastic (e=0.7): v_left changed from 2.0 to {robot1b.v_left:.2f}")
    
    assert robot1a.v_left == 0.0, "Inelastic collision should stop robot"
    assert robot1b.v_left < 0.0, "Elastic collision should reverse velocity"
    assert abs(robot1b.v_left - (-2.0 * 0.7)) < 0.01, "Elastic velocity should match elasticity"
    
    print("  Result: PASSED - Elasticity affects collisions correctly")
    
    return True


def main():
    """Run all Phase 2 tests."""
    print("\n" + "=" * 70)
    print("PHASE 2 ROBOT INTERACTION TEST SUITE")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Phase 2 Enabled: {ENABLE_PHASE2_INTERACTION}")
    print(f"  Collisions Enabled: {ROBOT_COLLISIONS_ENABLED}")
    print(f"  Communication Range Enabled: {COMMUNICATION_RANGE_ENABLED}")
    print(f"  Robot Radius: {ROBOT_RADIUS}")
    print(f"  Collision Elasticity: {COLLISION_ELASTICITY}")
    print(f"  Communication Range: {COMMUNICATION_RANGE}")
    
    tests = [
        test_collision_detection,
        test_collision_response,
        test_velocity_reversal,
        test_no_collision_when_far,
        test_communication_range,
        test_nearby_robots_info,
        test_integration_with_swarm,
        test_elasticity_effect,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            failed += 1
            print(f"  Result: FAILED - {e}")
        except Exception as e:
            failed += 1
            print(f"  Result: FAILED - Exception: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {len(tests)}")
    
    if failed == 0:
        print("\n[SUCCESS] All Phase 2 tests passed!")
        emoji = "🎉" if sys.stdout.encoding != 'cp1252' else "[OK]"
        print(f"{emoji} PHASE 2 ROBOT INTERACTION READY!")
    else:
        print(f"\n[ERROR] {failed} test(s) failed!")
    
    print("=" * 70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

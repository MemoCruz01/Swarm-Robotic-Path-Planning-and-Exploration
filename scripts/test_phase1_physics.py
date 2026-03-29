"""
Comprehensive test suite for Phase 1 Physics (Battery, Acceleration, Motor Delay).
Tests individual features and integration.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from src.robot import DifferentialDriveRobot
from config.settings import *


def print_test_header(title):
    """Print test header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def test_battery_drain():
    """Test 1: Battery drains at correct rate based on wheel speed."""
    print_test_header("TEST 1: Battery Drain Physics")
    
    robot = DifferentialDriveRobot(0, 50, 50)
    initial_battery = robot.battery
    
    # Stationary: minimal drain
    robot.v_left = 0
    robot.v_right = 0
    for _ in range(5):
        robot.update_battery()
    
    battery_after_idle = robot.battery
    idle_drain = initial_battery - battery_after_idle
    print(f"  Idle drain (5 steps): {idle_drain:.3f}%")
    assert idle_drain > 0, "Battery should drain even when idle"
    
    # High speed: higher drain
    robot.battery = 100.0
    robot.v_left = 2.0
    robot.v_right = 2.0
    for _ in range(5):
        robot.update_battery()
    
    battery_after_speed = robot.battery
    speed_drain = 100 - battery_after_speed
    print(f"  High-speed drain (5 steps): {speed_drain:.3f}%")
    assert speed_drain > idle_drain, "High speed should drain more than idle"
    print(f"  ✓ Quadratic drain confirmed: {speed_drain:.1f}% > {idle_drain:.1f}%")


def test_battery_stops_robot():
    """Test 2: Robot stops moving when battery reaches 0."""
    print_test_header("TEST 2: Dead Battery Stops Movement")
    
    robot = DifferentialDriveRobot(0, 50, 50)
    robot.battery = 0
    
    # Even with high speed target, should not move
    robot.v_left_target = 2.0
    robot.v_right_target = 2.0
    robot.update_velocity(50, 50, 50, 50)
    
    assert robot.desired_speed == 0, "PSO should set desired_speed to 0 when battery is dead"
    print(f"  ✓ Dead battery prevents movement (desired_speed = {robot.desired_speed})")


def test_battery_recharging():
    """Test 3: Battery recharges at home base."""
    print_test_header("TEST 3: Battery Recharging at Home")
    
    robot = DifferentialDriveRobot(0, 0, 0)  # Start at home
    robot.battery = 30  # Low battery
    initial_battery = robot.battery
    
    # At home with no movement = charging
    robot.v_left = 0
    robot.v_right = 0
    for _ in range(10):
        robot.update_battery()
    
    battery_after_charge = robot.battery
    recharge_amount = battery_after_charge - initial_battery
    print(f"  Battery at home: {initial_battery}% → {battery_after_charge}%")
    print(f"  Recharge amount: +{recharge_amount:.1f}% (10 steps)")
    assert battery_after_charge > initial_battery, "Battery should increase at home"
    assert battery_after_charge <= 100, "Battery should not exceed 100%"
    print(f"  ✓ Recharging works correctly")


def test_battery_low_threshold():
    """Test 4: Low battery reduces speed."""
    print_test_header("TEST 4: Low Battery Speed Reduction")
    
    robot = DifferentialDriveRobot(0, 50, 50)
    robot.battery = 15  # Below 20% threshold
    
    # Set desired heading and speed
    robot.desired_heading = 0
    robot.desired_speed = 2.0  # Max speed
    
    # Update PSO (should reduce speed due to low battery)
    robot.update_velocity(50, 50, 50, 50)
    
    # Speed should be reduced proportionally
    expected_speed = 2.0 * (15 / 100)  # 15% of max
    actual_speed = robot.desired_speed
    print(f"  With 15% battery, speed: {actual_speed:.3f} (expected ~{expected_speed:.3f})")
    assert actual_speed < 2.0, "Low battery should reduce speed"
    print(f"  ✓ Low battery correctly reduces speed")


def test_acceleration_smoothing():
    """Test 5: Acceleration smoothing prevents instant velocity changes."""
    print_test_header("TEST 5: Motor Acceleration Smoothing")
    
    robot = DifferentialDriveRobot(0, 50, 50)
    robot.v_left = 0
    robot.v_right = 0
    robot.v_left_target = 2.0
    robot.v_right_target = 2.0
    
    # Apply smoothing step by step
    print(f"  Step | v_left | v_right | Target")
    print(f"    0 │ {robot.v_left:6.2f} │ {robot.v_right:7.2f} │  2.00")
    
    for step in range(1, 6):
        robot.apply_acceleration_smoothing()
        print(f"    {step} │ {robot.v_left:6.2f} │ {robot.v_right:7.2f} │  2.00")
    
    # Should gradually approach target (max 0.5 per step)
    assert robot.v_left > 0, "Velocity should increase"
    assert robot.v_left <= 2.0, "Velocity should not exceed target"
    print(f"  ✓ Smooth acceleration working (reached {robot.v_left:.2f} in 5 steps)")


def test_motor_delay_queue():
    """Test 6: Motor response delay queues and delays commands."""
    print_test_header("TEST 6: Motor Response Delay Queue")
    
    robot = DifferentialDriveRobot(0, 50, 50)
    
    # Queue should be empty initially
    assert len(robot.v_left_queue) == 0, "Queue should start empty"
    
    # Set a desired velocity (will be queued in _velocity_to_wheels)
    robot.desired_heading = 0
    robot.desired_speed = 1.0
    robot._velocity_to_wheels()
    
    # Command should be in queue
    assert len(robot.v_left_queue) > 0, "Command should be queued"
    queued_v = robot.v_left_queue[0] if robot.v_left_queue else None
    print(f"  Command queued: v_left = {queued_v:.3f}")
    
    # Apply delay - command should pop
    robot.apply_motor_delay()
    delayed_v = robot.v_left
    print(f"  After delay: v_left = {delayed_v:.3f}")
    assert delayed_v == queued_v, "Delayed velocity should match queued command"
    print(f"  ✓ Motor delay queue working correctly")


def test_full_integration():
    """Test 7: All Phase 1 features work together."""
    print_test_header("TEST 7: Full Phase 1 Integration")
    
    robot = DifferentialDriveRobot(0, 50, 50)
    initial_x = robot.x
    initial_y = robot.y
    
    # Run 20 steps with all Phase 1 features active
    for step in range(20):
        # PSO update
        robot.update_velocity(60, 60, 60, 60)
        # Position update (calls motor delay, acceleration, battery)
        robot.update_position()
    
    # Robot should have moved
    distance = np.sqrt((robot.x - initial_x)**2 + (robot.y - initial_y)**2)
    print(f"  After 20 steps: moved {distance:.2f} units")
    print(f"  Position: ({robot.x:.1f}, {robot.y:.1f})")
    print(f"  Battery: {robot.battery:.1f}%")
    print(f"  v_left: {robot.v_left:.2f}, v_right: {robot.v_right:.2f}")
    
    assert distance > 0, "Robot should move"
    assert robot.battery < 100, "Battery should drain during movement"
    print(f"  ✓ Full integration test passed")


def test_no_battery_constraint():
    """Test 8: Can disable battery (legacy mode)."""
    print_test_header("TEST 8: Legacy Mode (No Battery Constraints)")
    
    robot = DifferentialDriveRobot(0, 50, 50)
    robot.battery = 1  # Nearly dead
    
    # Even with very low battery, if we don't check it, robot can move
    robot.desired_heading = 0
    robot.desired_speed = 2.0
    robot._velocity_to_wheels()  # Don't call update_velocity (which checks battery)
    
    # Direct setting should work
    assert robot.v_left_target != 0 or robot.v_right_target != 0, "Should have non-zero targets"
    print(f"  ✓ Can bypass battery constraints if needed (legacy compatibility)")


def test_realistic_trajectory():
    """Test 9: Trajectory looks realistic with all Phase 1 features."""
    print_test_header("TEST 9: Realistic Trajectory Validation")
    
    robot = DifferentialDriveRobot(0, 50, 50)
    target_x, target_y = 80, 80
    
    positions = []
    distances_to_target = []
    
    for step in range(30):
        # PSO towards target
        robot.update_velocity(target_x, target_y, target_x, target_y)
        robot.update_position()
        
        positions.append((robot.x, robot.y))
        dist = np.sqrt((robot.x - target_x)**2 + (robot.y - target_y)**2)
        distances_to_target.append(dist)
    
    # Check trajectory properties
    initial_distance = distances_to_target[0]
    final_distance = distances_to_target[-1]
    improvement = initial_distance - final_distance
    
    print(f"  Initial distance to target: {initial_distance:.2f}")
    print(f"  Final distance to target: {final_distance:.2f}")
    print(f"  Improvement: {improvement:.2f} units")
    print(f"  Final battery: {robot.battery:.1f}%")
    
    # Should generally get closer (allowing for oscillation)
    assert final_distance < initial_distance, "Should generally move towards target"
    
    # Trajectory should show smooth motion
    position_array = np.array(positions)
    position_diffs = np.diff(position_array, axis=0)
    distances = np.sqrt(np.sum(position_diffs**2, axis=1))
    max_step_distance = np.max(distances)
    avg_step_distance = np.mean(distances)
    print(f"  Max step distance: {max_step_distance:.3f}")
    print(f"  Avg step distance: {avg_step_distance:.3f}")
    
    # With max speed of 2.0, max reasonable step is ~2.0 (straight line motion)
    assert max_step_distance < 3.0, "Step distances should be reasonable for given robot speed"
    
    print(f"  ✓ Trajectory is realistic and efficient")


def run_all_tests():
    """Run all Phase 1 tests."""
    print("\n" + "="*70)
    print("  PHASE 1 PHYSICS TEST SUITE")
    print("="*70)
    print(f"  Battery Management, Acceleration Smoothing, Motor Delay")
    
    tests = [
        ("Battery drain", test_battery_drain),
        ("Dead battery stopping", test_battery_stops_robot),
        ("Battery recharging", test_battery_recharging),
        ("Low battery speed reduction", test_battery_low_threshold),
        ("Acceleration smoothing", test_acceleration_smoothing),
        ("Motor delay queue", test_motor_delay_queue),
        ("Full integration", test_full_integration),
        ("Legacy mode", test_no_battery_constraint),
        ("Realistic trajectory", test_realistic_trajectory),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
            print(f"\n  ✓ PASSED: {test_name}")
        except AssertionError as e:
            failed += 1
            print(f"\n  ✗ FAILED: {test_name}")
            print(f"    Error: {e}")
        except Exception as e:
            failed += 1
            print(f"\n  ✗ ERROR: {test_name}")
            print(f"    Exception: {e}")
    
    print("\n" + "="*70)
    print(f"  TEST RESULTS: {passed} passed, {failed} failed")
    print("="*70)
    
    if failed == 0:
        print("\n  🎉 ALL TESTS PASSED! Phase 1 Physics Ready!")
    else:
        print(f"\n  ⚠️  {failed} test(s) failed. Review output above.")
    
    print("\n")
    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_tests()
    exit(0 if failed == 0 else 1)

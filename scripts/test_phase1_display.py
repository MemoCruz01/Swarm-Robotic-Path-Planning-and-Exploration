"""
Test script to demonstrate Phase 1 metrics display in animation.
Shows how the Phase 1 physics stats appear in the animation panel.
"""

import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import *
from config.realism_settings import ENABLE_PHASE1_PHYSICS, BATTERY_ENABLED, BATTERY_LOW_THRESHOLD
from src.environment import Environment, Obstacle
from src.swarm import RobotSwarm


def create_test_environment():
    """Create test environment."""
    obstacles = []
    np.random.seed(42)  # Fixed seed for reproducibility
    
    for _ in range(NUM_OBSTACLES):
        while True:
            x = np.random.uniform(10, ENVIRONMENT_WIDTH - 10)
            y = np.random.uniform(10, ENVIRONMENT_HEIGHT - 10)
            radius = np.random.uniform(OBSTACLE_MIN_SIZE, OBSTACLE_MAX_SIZE)
            
            collision = False
            for obs in obstacles:
                dist = np.sqrt((obs.x - x)**2 + (obs.y - y)**2)
                if dist < (obs.radius + radius + 5):
                    collision = True
                    break
            
            if not collision:
                obstacles.append(Obstacle(x, y, radius))
                break
    
    env = Environment(
        ENVIRONMENT_WIDTH,
        ENVIRONMENT_HEIGHT,
        obstacles=obstacles,
        target_x=TARGET_X,
        target_y=TARGET_Y
    )
    
    return env


def get_phase1_stats(swarm):
    """Get Phase 1 physics statistics from swarm robots."""
    if not ENABLE_PHASE1_PHYSICS or not swarm.robots:
        return None
    
    batteries = []
    charging = 0
    low_battery = 0
    avg_queue_depth = []
    
    for robot in swarm.robots:
        if hasattr(robot, 'battery'):
            batteries.append(robot.battery)
            
            # Count charging robots (at home)
            if robot.x < 3.0 and robot.y < 3.0:
                charging += 1
            
            # Count low battery robots
            if robot.battery < BATTERY_LOW_THRESHOLD:
                low_battery += 1
            
            # Get motor delay queue depth
            if hasattr(robot, 'v_left_queue'):
                avg_queue_depth.append(len(robot.v_left_queue))
    
    if batteries:
        return {
            'avg_battery': np.mean(batteries),
            'min_battery': np.min(batteries),
            'max_battery': np.max(batteries),
            'charging_robots': charging,
            'low_battery_count': low_battery,
            'avg_queue_depth': np.mean(avg_queue_depth) if avg_queue_depth else 0
        }
    return None


def main():
    """Run test and display Phase 1 metrics."""
    print("\n" + "=" * 70)
    print("PHASE 1 METRICS DISPLAY TEST")
    print("=" * 70)
    print("\nConfiguration:")
    print(f"  Phase 1 Physics: {'ENABLED' if ENABLE_PHASE1_PHYSICS else 'DISABLED'}")
    print(f"  Battery System: {'ENABLED' if BATTERY_ENABLED else 'DISABLED'}")
    print(f"  Number of Robots: {NUM_ROBOTS}")
    print()
    
    # Create environment and swarm
    print("Initializing test environment...")
    environment = create_test_environment()
    swarm = RobotSwarm(NUM_ROBOTS, environment, ROBOT_SPEED, ROBOT_SENSOR_RANGE)
    print(f"[OK] Environment ready with {len(environment.obstacles)} obstacles")
    print(f"[OK] Swarm initialized with {NUM_ROBOTS} robots\n")
    
    print("Running simulation steps and displaying Phase 1 metrics...")
    print("=" * 70)
    
    # Run simulation for 20 steps and show metrics
    for step in range(20):
        step_data = swarm.step()
        phase1_stats = get_phase1_stats(swarm)
        
        # Display metrics every 5 steps
        if step % 5 == 0:
            print(f"\n--- Iteration {step_data['iteration']} ---")
            print(f"Best Fitness: {step_data['best_fitness']:.2f}")
            print(f"Exploration: {step_data['exploration_coverage']:.1f}%")
            print(f"Avg Robot Speed: {step_data['avg_robot_speed']:.2f}")
            
            if ENABLE_PHASE1_PHYSICS and phase1_stats:
                print(f"\nPHASE 1 PHYSICS DISPLAY:")
                print(f"{'='*40}")
                
                if BATTERY_ENABLED:
                    print(f"Battery Status:")
                    print(f"  Average: {phase1_stats['avg_battery']:.1f}%")
                    print(f"  Range: {phase1_stats['min_battery']:.1f}% - {phase1_stats['max_battery']:.1f}%")
                    
                    if phase1_stats['low_battery_count'] > 0:
                        print(f"  [!] Low Battery: {phase1_stats['low_battery_count']} robots")
                    
                    if phase1_stats['charging_robots'] > 0:
                        print(f"  [+] Charging at Home: {phase1_stats['charging_robots']} robots")
                
                if phase1_stats['avg_queue_depth'] > 0:
                    print(f"Motor Delay Queue: {phase1_stats['avg_queue_depth']:.1f} frames avg")
                
                print(f"{'='*40}")
    
    print("\n" + "=" * 70)
    print("DISPLAY TEST COMPLETE")
    print("=" * 70)
    print("\nIMPORTANT: These metrics are displayed in the animation window!")
    print("When you run 'python animate_swarm.py', you will see:")
    print("  - Battery levels (average, min, max)")
    print("  - Number of robots charging at home base")
    print("  - Number of robots with low battery")
    print("  - Motor delay queue depth")
    print("\nThese metrics update in real-time in the info panel during animation.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

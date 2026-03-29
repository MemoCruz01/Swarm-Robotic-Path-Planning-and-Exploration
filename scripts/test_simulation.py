"""
Quick test script for swarm robotics simulation without GUI.
Useful for testing the algorithm and performance metrics.
"""

import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

from config.settings import *
from src.environment import Environment, Obstacle
from src.swarm import RobotSwarm


def create_environment() -> Environment:
    """Create environment with obstacles and targets."""
    obstacles = []
    np.random.seed(RANDOM_SEED)
    
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


def run_quick_test(max_iterations: int = 200) -> dict:
    """
    Run a quick test simulation without GUI.
    
    Args:
        max_iterations: Number of iterations to run
        
    Returns:
        Dictionary with results
    """
    print("=" * 70)
    print("SWARM ROBOTICS - QUICK TEST (No GUI)")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Environment: {ENVIRONMENT_WIDTH}x{ENVIRONMENT_HEIGHT}")
    print(f"  Number of Robots: {NUM_ROBOTS}")
    print(f"  Number of Obstacles: {NUM_OBSTACLES}")
    print(f"  Target Position: ({TARGET_X}, {TARGET_Y})")
    print(f"  Test Duration: {max_iterations} iterations")
    print()
    
    # Create environment
    print("Creating environment...")
    environment = create_environment()
    print(f"  ✓ Created {len(environment.obstacles)} obstacles")
    
    # Create swarm
    print("Initializing swarm...")
    swarm = RobotSwarm(NUM_ROBOTS, environment, ROBOT_SPEED, ROBOT_SENSOR_RANGE)
    print(f"  ✓ Initialized {NUM_ROBOTS} robots")
    
    # Run simulation
    print("\nRunning simulation...")
    print(f"{'Iter':<8} {'Best Fit':<15} {'Explore %':<12} {'Near Target':<15} {'Status':<15}")
    print("-" * 70)
    
    for iteration in range(max_iterations):
        step_data = swarm.step()
        
        if iteration % 20 == 0 or step_data['target_found']:
            status = "✓ TARGET!" if step_data['target_found'] else "Running..."
            print(f"{iteration:<8} {step_data['best_fitness']:<15.2f} "
                  f"{step_data['exploration_coverage']:<11.1f}% "
                  f"{step_data['robots_near_target']:<15} {status:<15}")
        
        if step_data['target_found']:
            print("\n" + "=" * 70)
            print(f"✓ SUCCESS! Target found at iteration {iteration}")
            print("=" * 70)
            break
    
    # Final results
    final_data = step_data
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"Total iterations: {swarm.iteration}")
    print(f"Target found: {'Yes' if swarm.target_found else 'No'}")
    print(f"Final exploration coverage: {final_data['exploration_coverage']:.1f}%")
    print(f"Best fitness achieved: {final_data['best_fitness']:.2f}")
    print(f"Robots near target: {final_data['robots_near_target']}/{NUM_ROBOTS}")
    print(f"Swarm spread: {swarm.get_swarm_spread():.2f}")
    print(f"Swarm center: ({swarm.get_swarm_center()[0]:.1f}, {swarm.get_swarm_center()[1]:.1f})")
    print("=" * 70)
    
    return {
        'total_iterations': swarm.iteration,
        'target_found': swarm.target_found,
        'final_exploration': final_data['exploration_coverage'],
        'best_fitness': final_data['best_fitness'],
        'robots_near_target': final_data['robots_near_target']
    }


if __name__ == "__main__":
    print("\n" + "🤖 " * 20)
    results = run_quick_test(max_iterations=200)
    print("\n✓ Quick test completed successfully!")
    print("  Now run 'python scripts/main.py' to see full visualization with interactive plots\n")

"""
Main simulation script for swarm robotics path planning and exploration.
"""

import sys
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for GUI rendering
import matplotlib.pyplot as plt

from config.settings import *
from src.environment import Environment, Obstacle
from src.swarm import RobotSwarm
from src.visualization import SwarmVisualizer


def create_environment() -> Environment:
    """
    Create environment with obstacles and targets.
    
    Returns:
        Environment object
    """
    # Create random obstacles
    obstacles = []
    np.random.seed(RANDOM_SEED)
    
    for _ in range(NUM_OBSTACLES):
        while True:
            x = np.random.uniform(10, ENVIRONMENT_WIDTH - 10)
            y = np.random.uniform(10, ENVIRONMENT_HEIGHT - 10)
            radius = np.random.uniform(OBSTACLE_MIN_SIZE, OBSTACLE_MAX_SIZE)
            
            # Check collision with other obstacles
            collision = False
            for obs in obstacles:
                dist = np.sqrt((obs.x - x)**2 + (obs.y - y)**2)
                if dist < (obs.radius + radius + 5):
                    collision = True
                    break
            
            if not collision:
                obstacles.append(Obstacle(x, y, radius))
                break
    
    # Create environment
    env = Environment(
        ENVIRONMENT_WIDTH,
        ENVIRONMENT_HEIGHT,
        obstacles=obstacles,
        target_x=TARGET_X,
        target_y=TARGET_Y
    )
    
    # Initialize Phase 4 features if enabled
    if env.phase4_enabled:
        if env.terrain_system is not None:
            # Create random terrain zones
            env.terrain_system.create_random_terrain(num_friction=3, num_slippy=1)
            terrain_stats = env.terrain_system.get_statistics()
            print(f"  ✓ Created {terrain_stats['total_zones']} terrain zones")
        
        if env.dynamic_obstacles is not None:
            # Spawn initial dynamic obstacles
            from config.realism_settings import DYNAMIC_OBSTACLE_COUNT
            for _ in range(DYNAMIC_OBSTACLE_COUNT):
                env.dynamic_obstacles.spawn_random_obstacle(min_distance=40)
            print(f"  ✓ Spawned {len(env.dynamic_obstacles.obstacles)} dynamic obstacles")
    
    return env


def run_simulation(max_iterations: int = PSO_ITERATIONS,
                   visualize: bool = True,
                   save_animation: bool = False) -> dict:
    """
    Run the main simulation.
    
    Args:
        max_iterations: Maximum number of iterations
        visualize: Whether to show visualization
        save_animation: Whether to save animation to file
        
    Returns:
        Dictionary with simulation results
    """
    print("=" * 60)
    print("Swarm Robotics Path Planning and Exploration Simulation")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Environment: {ENVIRONMENT_WIDTH}x{ENVIRONMENT_HEIGHT}")
    print(f"  Number of Robots: {NUM_ROBOTS}")
    print(f"  Number of Obstacles: {NUM_OBSTACLES}")
    print(f"  Target Position: ({TARGET_X}, {TARGET_Y})")
    print(f"  Max Iterations: {max_iterations}")
    print()
    
    # Create environment
    print("Creating environment with obstacles...")
    environment = create_environment()
    print(f"  ✓ Created {len(environment.obstacles)} obstacles")
    print(f"  ✓ Target at ({environment.target_x}, {environment.target_y})")
    
    # Create swarm
    print("\nInitializing robot swarm...")
    swarm = RobotSwarm(
        NUM_ROBOTS,
        environment,
        robot_speed=ROBOT_SPEED,
        sensor_range=ROBOT_SENSOR_RANGE
    )
    print(f"  ✓ Initialized {NUM_ROBOTS} robots")
    
    # Initialize visualizer
    print("\nInitializing visualization...")
    visualizer = SwarmVisualizer(swarm, environment)
    print("  ✓ Visualization ready")
    
    # Run simulation
    print("\nRunning simulation...")
    print(f"{'Iteration':<12} {'Best Fitness':<20} {'Exploration':<15} {'Near Target':<12}")
    print("-" * 60)
    
    simulation_data = []
    iteration = 0
    
    try:
        for iteration in range(max_iterations):
            # Execute simulation step
            step_data = swarm.step()
            simulation_data.append(step_data)
            
            # Print progress every VISUALIZATION_INTERVAL iterations
            if iteration % VISUALIZATION_INTERVAL == 0:
                print(f"{iteration:<12} {step_data['best_fitness']:<20.2f} "
                      f"{step_data['exploration_coverage']:<14.1f}% "
                      f"{step_data['robots_near_target']:<12}")
            
            # Check if target found
            if step_data['target_found']:
                print(f"\n✓ TARGET FOUND at iteration {step_data['iteration']}!")
                break
        
        print("-" * 60)
        print(f"\nSimulation completed!")
        print(f"  Total iterations: {iteration + 1}")
        print(f"  Final exploration coverage: {simulation_data[-1]['exploration_coverage']:.1f}%")
        print(f"  Best fitness achieved: {simulation_data[-1]['best_fitness']:.2f}")
        
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user")
    
    # Visualization
    if visualize and len(simulation_data) > 0:
        print("\nGenerating animation...")
        if SHOW_VELOCITY_VECTORS:
            print("  ✓ Showing velocity vectors")
        
        # Show final state
        visualizer.show_static(simulation_data[-1])
        
        # Plot convergence metrics
        print("\nPlotting convergence metrics...")
        visualizer.plot_convergence()
        
        # Optionally save animation
        if save_animation:
            print("\nSaving animation...")
            visualizer.save_animation(
                simulation_data,
                'swarm_simulation.gif',
                interval=ANIMATION_SPEED,
                fps=10
            )
    
    # Compile results
    results = {
        'total_iterations': len(simulation_data),
        'target_found': swarm.target_found,
        'target_found_iteration': swarm.target_found_iteration,
        'final_exploration_coverage': simulation_data[-1]['exploration_coverage'] if simulation_data else 0,
        'best_fitness': swarm.pso.global_best_fitness,
        'convergence_metrics': swarm.pso.get_convergence_metrics(),
        'simulation_data': simulation_data
    }
    
    return results


def print_results(results: dict):
    """Print simulation results summary."""
    print("\n" + "=" * 60)
    print("SIMULATION RESULTS")
    print("=" * 60)
    print(f"Total Iterations: {results['total_iterations']}")
    print(f"Target Found: {'Yes' if results['target_found'] else 'No'}")
    if results['target_found']:
        print(f"Target Found at Iteration: {results['target_found_iteration']}")
    print(f"Final Exploration Coverage: {results['final_exploration_coverage']:.1f}%")
    print(f"Best Fitness Achieved: {results['best_fitness']:.2f}")
    print("\nConvergence Metrics:")
    for key, value in results['convergence_metrics'].items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    print("=" * 60)


if __name__ == "__main__":
    # Run simulation with full visualization and animation
    results = run_simulation(
        max_iterations=PSO_ITERATIONS,
        visualize=True,
        save_animation=False  # Set to True to save .gif animation
    )
    
    # Print results summary
    print_results(results)

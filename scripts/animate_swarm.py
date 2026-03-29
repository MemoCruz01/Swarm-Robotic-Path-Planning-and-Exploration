"""
Live animated visualization of swarm robotics simulation.
Shows the swarm moving in real-time with interactive controls.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection

from config.settings import *
from src.environment import Environment, Obstacle
from src.swarm import RobotSwarm


def create_environment() -> Environment:
    """Create environment with obstacles."""
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


def run_live_simulation():
    """Run simulation with live animation of swarm movement."""
    
    print("=" * 70)
    print("SWARM ROBOTICS - LIVE ANIMATED SIMULATION")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Environment: {ENVIRONMENT_WIDTH}x{ENVIRONMENT_HEIGHT}")
    print(f"  Number of Robots: {NUM_ROBOTS}")
    print(f"  Number of Obstacles: {NUM_OBSTACLES}")
    print(f"  Target Position: ({TARGET_X}, {TARGET_Y})")
    print()
    
    # Create environment and swarm
    print("Initializing simulation...")
    environment = create_environment()
    swarm = RobotSwarm(NUM_ROBOTS, environment, ROBOT_SPEED, ROBOT_SENSOR_RANGE)
    print(f"✓ Environment ready with {len(environment.obstacles)} obstacles")
    print(f"✓ Swarm initialized with {NUM_ROBOTS} robots\n")
    
    # Setup figure
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, ENVIRONMENT_WIDTH)
    ax.set_ylim(0, ENVIRONMENT_HEIGHT)
    ax.set_aspect('equal')
    ax.set_title('Swarm Robotics - Live Exploration Animation', fontsize=14, fontweight='bold')
    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    ax.grid(True, alpha=0.2)
    
    # Draw obstacles
    for obstacle in environment.obstacles:
        circle = patches.Circle(
            (obstacle.x, obstacle.y),
            obstacle.radius,
            color='gray',
            alpha=0.6,
            zorder=3,
            label='Obstacles' if obstacle == environment.obstacles[0] else ''
        )
        ax.add_patch(circle)
    
    # Draw target
    target_circle = patches.Circle(
        (environment.target_x, environment.target_y),
        5.0,
        color='red',
        alpha=0.8,
        label='Target',
        zorder=4
    )
    ax.add_patch(target_circle)
    
    # Animation artists
    robot_scatter = ax.scatter([], [], s=150, c='blue', alpha=0.7, label='Robots', zorder=5)
    swarm_center = ax.plot([], [], 'b*', markersize=20, label='Swarm Center', zorder=6)[0]
    velocity_quiver = None
    
    # Text info
    info_text = ax.text(0.02, 0.98, '', transform=ax.transAxes,
                       fontsize=10, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                       family='monospace')
    
    # Legend
    ax.legend(loc='upper left', fontsize=10)
    
    # Storage for data and state
    state = {
        'data': [],
        'target_found': False,
        'iteration': 0
    }
    
    def animate(frame):
        """Animation function called for each frame."""
        # Stop if target already found
        if state['target_found']:
            return robot_scatter, swarm_center, info_text
        
        # Run simulation step
        step_data = swarm.step()
        state['data'].append(step_data)
        state['iteration'] = step_data['iteration']
        state['target_found'] = step_data['target_found']
        
        # Update robot positions
        positions = swarm.get_robot_positions()
        if positions:
            xs, ys = zip(*positions)
            robot_scatter.set_offsets(np.c_[xs, ys])
        
        # Update swarm center
        center_x, center_y = swarm.get_swarm_center()
        swarm_center.set_data([center_x], [center_y])
        
        # Update velocity vectors (every few frames for clarity)
        nonlocal velocity_quiver
        if frame % 3 == 0:  # Show every 3rd frame
            if velocity_quiver:
                velocity_quiver.remove()
            
            velocities = swarm.get_robot_velocities()
            if velocities and positions:
                vxs, vys = zip(*velocities)
                velocity_quiver = ax.quiver(
                    xs, ys, vxs, vys,
                    color='cyan', alpha=0.4, scale=50, zorder=4
                )
        
        # Update info text
        info_str = (
            f"Iteration: {step_data['iteration']}\n"
            f"Best Fitness: {step_data['best_fitness']:.2f}\n"
            f"Exploration: {step_data['exploration_coverage']:.1f}%\n"
            f"Robots Near Target: {step_data['robots_near_target']}/{NUM_ROBOTS}\n"
            f"Avg Speed: {step_data['avg_robot_speed']:.2f}\n"
            f"Swarm Spread: {swarm.get_swarm_spread():.2f}\n"
        )
        
        if step_data['target_found']:
            info_str += "\n✓ TARGET FOUND!"
            ax.set_title('✓ TARGET FOUND! - Live Exploration Animation', 
                        fontsize=14, fontweight='bold', color='green')
        
        info_text.set_text(info_str)
        
        # Stop animation if target found
        if step_data['target_found']:
            return robot_scatter, swarm_center, info_text
        
        return robot_scatter, swarm_center, info_text
    
    # Create animation
    max_frames = PSO_ITERATIONS
    anim = animation.FuncAnimation(
        fig, animate,
        frames=max_frames,
        interval=50,  # 50ms per frame = 20 FPS
        blit=False,
        repeat=True
    )
    
    plt.tight_layout()
    plt.show()
    
    # Print final results
    if state['data']:
        final = state['data'][-1]
        print("\n" + "=" * 70)
        print("SIMULATION RESULTS")
        print("=" * 70)
        print(f"Total Iterations: {final['iteration']}")
        print(f"Target Found: {'YES ✓' if final['target_found'] else 'NO ✗'}")
        print(f"Robots in Target: {final['robots_near_target']}/{NUM_ROBOTS}")
        print(f"Final Exploration Coverage: {final['exploration_coverage']:.1f}%")
        print(f"Best Fitness Achieved: {final['best_fitness']:.2f}")
        print(f"Swarm Spread: {swarm.get_swarm_spread():.2f}")
        print("=" * 70)


if __name__ == "__main__":
    run_live_simulation()

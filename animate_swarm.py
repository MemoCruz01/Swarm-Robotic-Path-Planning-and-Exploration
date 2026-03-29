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
from config.realism_settings import (
    ENABLE_PHASE1_PHYSICS, BATTERY_ENABLED, BATTERY_LOW_THRESHOLD,
    ENABLE_PHASE2_INTERACTION, ROBOT_COLLISIONS_ENABLED, 
    COMMUNICATION_RANGE_ENABLED, COMMUNICATION_RANGE, ROBOT_RADIUS
)
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


def get_phase2_stats(swarm):
    """Get Phase 2 robot interaction statistics."""
    if not ENABLE_PHASE2_INTERACTION or not swarm.robots:
        return None
    
    stats = {}
    
    # Calculate robot spacing metrics
    if len(swarm.robots) >= 2:
        min_dist = float('inf')
        total_dist = 0
        pair_count = 0
        
        for i in range(len(swarm.robots)):
            for j in range(i + 1, len(swarm.robots)):
                r1 = swarm.robots[i]
                r2 = swarm.robots[j]
                
                dx = r2.x - r1.x
                dy = r2.y - r1.y
                dist = np.sqrt(dx**2 + dy**2)
                
                min_dist = min(min_dist, dist)
                total_dist += dist
                pair_count += 1
        
        stats['min_spacing'] = min_dist if min_dist != float('inf') else 0
        stats['avg_spacing'] = total_dist / pair_count if pair_count > 0 else 0
        stats['collision_threshold'] = 2.0 * ROBOT_RADIUS
    else:
        stats['min_spacing'] = 0
        stats['avg_spacing'] = 0
        stats['collision_threshold'] = 2.0 * ROBOT_RADIUS
    
    # Calculate communication statistics
    if COMMUNICATION_RANGE_ENABLED:
        total_neighbors = 0
        comm_pairs = 0
        
        for robot in swarm.robots:
            nearby = swarm.get_nearby_robots(robot.id, communication_range=COMMUNICATION_RANGE)
            total_neighbors += len(nearby)
            comm_pairs += len(nearby)
        
        stats['avg_communication_neighbors'] = total_neighbors / len(swarm.robots) if swarm.robots else 0
        stats['communication_pairs'] = comm_pairs // 2  # Each pair counted twice
    else:
        stats['avg_communication_neighbors'] = 0
        stats['communication_pairs'] = 0
    
    # Collision count (if not stored, estimate from frame)
    stats['collisions_estimated'] = 0  # Could be enhanced with collision logging
    
    return stats


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
    print(f"[OK] Environment ready with {len(environment.obstacles)} obstacles")
    print(f"[OK] Swarm initialized with {NUM_ROBOTS} robots\n")
    
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
        
        # Add Phase 1 statistics if enabled
        if ENABLE_PHASE1_PHYSICS:
            phase1_stats = get_phase1_stats(swarm)
            if phase1_stats:
                info_str += (
                    f"\n{'='*25}\n"
                    f"PHASE 1 PHYSICS STATUS\n"
                    f"{'='*25}\n"
                )
                if BATTERY_ENABLED:
                    info_str += (
                        f"Battery (avg): {phase1_stats['avg_battery']:.1f}%\n"
                        f"  Min: {phase1_stats['min_battery']:.1f}%  "
                        f"Max: {phase1_stats['max_battery']:.1f}%\n"
                    )
                    if phase1_stats['low_battery_count'] > 0:
                        info_str += f"  [!] Low battery: {phase1_stats['low_battery_count']} robots\n"
                    if phase1_stats['charging_robots'] > 0:
                        info_str += f"  [+] Charging: {phase1_stats['charging_robots']} robots\n"
                
                if phase1_stats['avg_queue_depth'] > 0:
                    info_str += f"Motor Delay (queue): {phase1_stats['avg_queue_depth']:.1f} frames\n"
        
        # Add Phase 2 statistics if enabled
        if ENABLE_PHASE2_INTERACTION:
            phase2_stats = get_phase2_stats(swarm)
            if phase2_stats:
                info_str += (
                    f"\n{'='*25}\n"
                    f"PHASE 2 INTERACTIONS\n"
                    f"{'='*25}\n"
                )
                
                if ROBOT_COLLISIONS_ENABLED:
                    info_str += (
                        f"Robot Spacing:\n"
                        f"  Min: {phase2_stats['min_spacing']:.2f} units\n"
                        f"  Avg: {phase2_stats['avg_spacing']:.2f} units\n"
                        f"  Threshold: {phase2_stats['collision_threshold']:.2f} units\n"
                    )
                    
                    # Simple collision warning
                    if phase2_stats['min_spacing'] < phase2_stats['collision_threshold'] * 1.2:
                        info_str += f"  [ACTIVE] Collisions in progress!\n"
                
                if COMMUNICATION_RANGE_ENABLED:
                    info_str += (
                        f"Communication Range ({COMMUNICATION_RANGE:.1f}u):\n"
                        f"  Avg Neighbors: {phase2_stats['avg_communication_neighbors']:.1f}\n"
                        f"  Active Pairs: {phase2_stats['communication_pairs']}\n"
                    )
        
        if step_data['target_found']:
            info_str += "\n[SUCCESS] TARGET FOUND!"
            ax.set_title('[SUCCESS] TARGET FOUND! - Live Exploration Animation', 
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
        print(f"Total Iterations: {state['iteration']}")
        print(f"Target Found: {'YES' if state['target_found'] else 'NO'}")
        print(f"Final Exploration Coverage: {final['exploration_coverage']:.1f}%")
        print(f"Best Fitness Achieved: {final['best_fitness']:.2f}")
        print(f"Robots Near Target: {final['robots_near_target']}/{NUM_ROBOTS}")
        print(f"Swarm Spread: {swarm.get_swarm_spread():.2f}")
        print("=" * 70)


if __name__ == "__main__":
    run_live_simulation()

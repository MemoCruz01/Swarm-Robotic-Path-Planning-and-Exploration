"""
Save swarm robotics simulation as video file (GIF with Phase 1 metrics).
Outputs are saved to outputs/animations/ directory with timestamped filenames.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import os
from datetime import datetime

from config.settings import *
from config.realism_settings import (
    ENABLE_PHASE1_PHYSICS, BATTERY_ENABLED, BATTERY_LOW_THRESHOLD,
    ENABLE_PHASE2_INTERACTION, ROBOT_COLLISIONS_ENABLED,
    COMMUNICATION_RANGE_ENABLED, COMMUNICATION_RANGE, ROBOT_RADIUS
)
from src.environment import Environment, Obstacle
from src.swarm import RobotSwarm


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
            if robot.x < 3.0 and robot.y < 3.0:
                charging += 1
            if robot.battery < BATTERY_LOW_THRESHOLD:
                low_battery += 1
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
    
    if COMMUNICATION_RANGE_ENABLED:
        total_neighbors = 0
        comm_pairs = 0
        
        for robot in swarm.robots:
            nearby = swarm.get_nearby_robots(robot.id, communication_range=COMMUNICATION_RANGE)
            total_neighbors += len(nearby)
            comm_pairs += len(nearby)
        
        stats['avg_communication_neighbors'] = total_neighbors / len(swarm.robots) if swarm.robots else 0
        stats['communication_pairs'] = comm_pairs // 2
    else:
        stats['avg_communication_neighbors'] = 0
        stats['communication_pairs'] = 0
    
    stats['collisions_estimated'] = 0
    return stats


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
            if robot.x < 3.0 and robot.y < 3.0:
                charging += 1
            if robot.battery < BATTERY_LOW_THRESHOLD:
                low_battery += 1
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


def save_animation_video(output_dir="outputs/animations", fps=20, save_mp4=False):
    """
    Save swarm simulation as video file with Phase 1 metrics.
    
    Args:
        output_dir: Output directory (default: outputs/animations)
        fps: Frames per second
        save_mp4: Also try to save as MP4 (requires ffmpeg)
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_file = f"swarm_simulation_{timestamp}"
    
    print("=" * 70)
    print("SWARM ROBOTICS - VIDEO SAVING MODE WITH PHASE 1 & 2 METRICS")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Environment: {ENVIRONMENT_WIDTH}x{ENVIRONMENT_HEIGHT}")
    print(f"  Number of Robots: {NUM_ROBOTS}")
    print(f"  Number of Obstacles: {NUM_OBSTACLES}")
    print(f"  Target Position: ({TARGET_X}, {TARGET_Y})")
    print(f"  Phase 1 Physics: {'ENABLED' if ENABLE_PHASE1_PHYSICS else 'DISABLED'}")
    print(f"  Phase 2 Interactions: {'ENABLED' if ENABLE_PHASE2_INTERACTION else 'DISABLED'}")
    print(f"\nVideo Settings:")
    print(f"  FPS: {fps}")
    print(f"  Output Directory: {output_dir}")
    print(f"  Output Filename: {output_file}.gif")
    if save_mp4:
        print(f"  Also attempting: {output_file}.mp4")
    print()
    
    # Create environment and swarm
    print("Initializing simulation...")
    environment = create_environment()
    swarm = RobotSwarm(NUM_ROBOTS, environment, ROBOT_SPEED, ROBOT_SENSOR_RANGE)
    print(f"[OK] Environment ready with {len(environment.obstacles)} obstacles")
    print(f"[OK] Swarm initialized with {NUM_ROBOTS} robots\n")
    
    # Setup figure
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, ENVIRONMENT_WIDTH)
    ax.set_ylim(0, ENVIRONMENT_HEIGHT)
    ax.set_aspect('equal')
    title = 'Swarm Robotics - Path Planning and Exploration'
    if ENABLE_PHASE1_PHYSICS:
        title += ' [PHASE 1 PHYSICS]'
    if ENABLE_PHASE2_INTERACTION:
        title += ' [PHASE 2 INTERACTIONS]'
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('X Position', fontsize=11)
    ax.set_ylabel('Y Position', fontsize=11)
    ax.grid(True, alpha=0.2)
    
    # Draw obstacles
    for obstacle in environment.obstacles:
        circle = patches.Circle(
            (obstacle.x, obstacle.y),
            obstacle.radius,
            color='gray',
            alpha=0.6,
            zorder=3
        )
        ax.add_patch(circle)
    
    # Draw target
    target_circle = patches.Circle(
        (environment.target_x, environment.target_y),
        5.0,
        color='red',
        alpha=0.8,
        zorder=4
    )
    ax.add_patch(target_circle)
    
    # Add legend labels
    ax.scatter([], [], s=150, c='blue', alpha=0.7, label='Robots')
    ax.scatter([], [], s=200, c='gray', alpha=0.6, label='Obstacles')
    ax.scatter([], [], s=200, c='red', alpha=0.8, label='Target')
    ax.plot([], [], 'b*', markersize=20, label='Swarm Center')
    
    # Animation artists
    robot_scatter = ax.scatter([], [], s=150, c='blue', alpha=0.7, zorder=5)
    swarm_center = ax.plot([], [], 'b*', markersize=20, zorder=6)[0]
    velocity_quiver = None
    
    # Text info
    info_text = ax.text(0.02, 0.98, '', transform=ax.transAxes,
                       fontsize=9, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                       family='monospace')
    
    # Legend
    ax.legend(loc='upper right', fontsize=10)
    
    # Storage for data and state
    state = {
        'target_found': False,
        'iteration': 0,
        'final_data': None
    }
    
    def animate(frame):
        """Animation function called for each frame."""
        # Stop if target already found
        if state['target_found']:
            return robot_scatter, swarm_center, info_text
        
        # Run simulation step
        step_data = swarm.step()
        state['iteration'] = step_data['iteration']
        state['target_found'] = step_data['target_found']
        state['final_data'] = step_data
        
        # Update robot positions
        positions = swarm.get_robot_positions()
        if positions:
            xs, ys = zip(*positions)
            robot_scatter.set_offsets(np.c_[xs, ys])
        
        # Update swarm center
        center_x, center_y = swarm.get_swarm_center()
        swarm_center.set_data([center_x], [center_y])
        
        # Update velocity vectors
        nonlocal velocity_quiver
        if frame % 3 == 0:
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
            f"Iteration: {step_data['iteration']:3d}  |  "
            f"Fitness: {step_data['best_fitness']:7.2f}  |  "
            f"Coverage: {step_data['exploration_coverage']:5.1f}%  |  "
            f"Near Target: {step_data['robots_near_target']:2d}/{NUM_ROBOTS}\n"
            f"Speed: {step_data['avg_robot_speed']:5.2f}  |  "
            f"Spread: {swarm.get_swarm_spread():5.2f}  |  "
            f"Position: ({center_x:6.1f}, {center_y:6.1f})"
        )
        
        # Add Phase 1 statistics if enabled
        if ENABLE_PHASE1_PHYSICS:
            phase1_stats = get_phase1_stats(swarm)
            if phase1_stats:
                info_str += "\n"
                if BATTERY_ENABLED:
                    info_str += f"Battery (avg): {phase1_stats['avg_battery']:.1f}%  "
                    info_str += f"Min: {phase1_stats['min_battery']:.1f}%  Max: {phase1_stats['max_battery']:.1f}%"
                    if phase1_stats['charging_robots'] > 0:
                        info_str += f"  |  Charging: {phase1_stats['charging_robots']}"
        
        # Add Phase 2 statistics if enabled
        if ENABLE_PHASE2_INTERACTION:
            phase2_stats = get_phase2_stats(swarm)
            if phase2_stats:
                info_str += "\n"
                if ROBOT_COLLISIONS_ENABLED:
                    info_str += (
                        f"Spacing: Min={phase2_stats['min_spacing']:.2f}u  "
                        f"Avg={phase2_stats['avg_spacing']:.2f}u  "
                    )
                    if phase2_stats['min_spacing'] < phase2_stats['collision_threshold'] * 1.2:
                        info_str += "[ACTIVE COLLISION]"
                
                if COMMUNICATION_RANGE_ENABLED:
                    info_str += (
                        f"  |  Comm: {phase2_stats['avg_communication_neighbors']:.1f} avg neighbors  "
                        f"{phase2_stats['communication_pairs']} pairs"
                    )
        
        if step_data['target_found']:
            info_str += "\n[SUCCESS] TARGET FOUND!"
            ax.set_title('[SUCCESS] TARGET FOUND! - Swarm Robotics Path Planning and Exploration', 
                        fontsize=14, fontweight='bold', color='green')
        
        info_text.set_text(info_str)
        
        # Print progress
        if frame % 100 == 0 or step_data['target_found']:
            print(f"  Frame {frame:3d} | Iteration {step_data['iteration']:3d} | "
                  f"Fitness: {step_data['best_fitness']:7.2f} | "
                  f"Coverage: {step_data['exploration_coverage']:5.1f}% | "
                  f"Near Target: {step_data['robots_near_target']}/{NUM_ROBOTS}")
        
        # Stop animation if target found
        if step_data['target_found']:
            return robot_scatter, swarm_center, info_text
        
        return robot_scatter, swarm_center, info_text
    
    # Create animation
    print("Rendering animation frames (this may take a minute)...\n")
    max_frames = PSO_ITERATIONS if not state['target_found'] else PSO_ITERATIONS
    
    anim = animation.FuncAnimation(
        fig, animate,
        frames=max_frames,
        interval=1000/fps,  # Convert fps to milliseconds
        blit=False,
        repeat=False
    )
    
    # Save as GIF
    print("\n" + "=" * 70)
    print("SAVING ANIMATION...")
    print("=" * 70)
    
    gif_file = os.path.join(output_dir, f"{output_file}.gif")
    print(f"\nSaving GIF: {gif_file}")
    print("(This may take a few minutes for smooth animation...)")
    
    try:
        anim.save(gif_file, writer='pillow', fps=fps, dpi=80)
        file_size_mb = os.path.getsize(gif_file) / (1024*1024)
        print(f"[SUCCESS] GIF saved successfully: {gif_file}")
        print(f"  File size: {file_size_mb:.1f} MB")
        print(f"  Location: {os.path.abspath(gif_file)}")
    except Exception as e:
        print(f"[ERROR] Failed to save GIF: {e}")
    
    # Try to save as MP4 if ffmpeg available
    if save_mp4:
        mp4_file = os.path.join(output_dir, f"{output_file}.mp4")
        print(f"\nSaving MP4: {mp4_file}")
        try:
            anim.save(mp4_file, writer='ffmpeg', fps=fps, dpi=80)
            print(f"[SUCCESS] MP4 saved successfully: {mp4_file}")
            print(f"  File size: {os.path.getsize(mp4_file) / (1024*1024):.1f} MB")
        except Exception as e:
            print(f"[INFO] MP4 not saved (ffmpeg may not be installed)")
            print(f"  Error: {e}")
    
    plt.close(fig)
    
    # Print results
    if state['final_data']:
        final = state['final_data']
        print("\n" + "=" * 70)
        print("SIMULATION RESULTS")
        print("=" * 70)
        print(f"Total Iterations: {final['iteration']}")
        print(f"Target Found: {'YES' if final['target_found'] else 'NO'}")
        print(f"Robots in Target: {final['robots_near_target']}/{NUM_ROBOTS}")
        print(f"Final Exploration Coverage: {final['exploration_coverage']:.1f}%")
        print(f"Best Fitness Achieved: {final['best_fitness']:.2f}")
        print(f"Swarm Spread: {swarm.get_swarm_spread():.2f}")
        print("=" * 70)


if __name__ == "__main__":
    save_animation_video()

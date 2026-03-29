"""
Save swarm robotics simulation as video file (MP4 and GIF).
Each run creates a unique timestamped file, allowing evolution tracking.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import os
from datetime import datetime

from config.settings import *
from config.realism_settings import (
    ENABLE_PHASE2_INTERACTION,
    ROBOT_COLLISIONS_ENABLED,
    COLLISION_ELASTICITY,
    ROBOT_RADIUS,
    COMMUNICATION_RANGE_ENABLED,
    COMMUNICATION_RANGE,
    ENABLE_PHASE3_NAVIGATION,
    USE_DWA,
    DWA_PREDICTION_STEPS,
)
from src.environment import Environment, Obstacle
from src.swarm import RobotSwarm


def get_phase2_stats(swarm):
    """
    Calculate Phase 2 robot interaction metrics.
    
    Returns:
        Dictionary with collision and communication statistics
    """
    if not ENABLE_PHASE2_INTERACTION:
        return None
    
    positions = swarm.get_robot_positions()
    if not positions or len(positions) < 2:
        return {
            'min_spacing': 999.0,
            'avg_spacing': 999.0,
            'collision_threshold': 2 * ROBOT_RADIUS,
            'avg_communication_neighbors': 0,
            'communication_pairs': 0,
            'active_collision': False
        }
    
    # Calculate min and avg spacing between all robot pairs
    distances = []
    collision_threshold = 2 * ROBOT_RADIUS
    
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            dx = positions[i][0] - positions[j][0]
            dy = positions[i][1] - positions[j][1]
            dist = np.sqrt(dx*dx + dy*dy)
            distances.append(dist)
    
    min_spacing = min(distances) if distances else 999.0
    avg_spacing = np.mean(distances) if distances else 999.0
    
    # Calculate communication metrics
    avg_neighbors = 0
    communication_pairs = 0
    
    if COMMUNICATION_RANGE_ENABLED:
        for i in range(len(positions)):
            neighbor_count = 0
            for j in range(len(positions)):
                if i != j:
                    dx = positions[i][0] - positions[j][0]
                    dy = positions[i][1] - positions[j][1]
                    dist = np.sqrt(dx*dx + dy*dy)
                    if dist <= COMMUNICATION_RANGE:
                        neighbor_count += 1
                        communication_pairs += 1
            avg_neighbors += neighbor_count
        
        avg_neighbors = avg_neighbors / len(positions) if positions else 0
        communication_pairs = communication_pairs // 2  # Each pair counted twice
    
    return {
        'min_spacing': min_spacing,
        'avg_spacing': avg_spacing,
        'collision_threshold': collision_threshold,
        'avg_communication_neighbors': avg_neighbors,
        'communication_pairs': communication_pairs,
        'active_collision': min_spacing < (collision_threshold * 1.2)
    }


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


def get_phase2_stats(swarm):
    """
    Calculate Phase 2 robot interaction metrics.
    
    Returns:
        Dictionary with collision and communication statistics
    """
    if not ENABLE_PHASE2_INTERACTION:
        return None
    
    positions = swarm.get_robot_positions()
    if not positions or len(positions) < 2:
        return {
            'min_spacing': 999.0,
            'avg_spacing': 999.0,
            'collision_threshold': 2 * ROBOT_RADIUS,
            'avg_communication_neighbors': 0,
            'communication_pairs': 0,
            'active_collision': False
        }
    
    # Calculate min and avg spacing between all robot pairs
    distances = []
    collision_threshold = 2 * ROBOT_RADIUS
    
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            dx = positions[i][0] - positions[j][0]
            dy = positions[i][1] - positions[j][1]
            dist = np.sqrt(dx*dx + dy*dy)
            distances.append(dist)
    
    min_spacing = min(distances) if distances else 999.0
    avg_spacing = np.mean(distances) if distances else 999.0
    
    # Calculate communication metrics
    avg_neighbors = 0
    communication_pairs = 0
    
    if COMMUNICATION_RANGE_ENABLED:
        for i in range(len(positions)):
            neighbor_count = 0
            for j in range(len(positions)):
                if i != j:
                    dx = positions[i][0] - positions[j][0]
                    dy = positions[i][1] - positions[j][1]
                    dist = np.sqrt(dx*dx + dy*dy)
                    if dist <= COMMUNICATION_RANGE:
                        neighbor_count += 1
                        communication_pairs += 1
            avg_neighbors += neighbor_count
        
        avg_neighbors = avg_neighbors / len(positions) if positions else 0
        communication_pairs = communication_pairs // 2  # Each pair counted twice
    
    return {
        'min_spacing': min_spacing,
        'avg_spacing': avg_spacing,
        'collision_threshold': collision_threshold,
        'avg_communication_neighbors': avg_neighbors,
        'communication_pairs': communication_pairs,
        'active_collision': min_spacing < (collision_threshold * 1.2)
    }


def get_phase3_stats(swarm):
    """
    Calculate Phase 3 DWA navigation metrics.
    
    Returns:
        Dictionary with DWA planning statistics
    """
    if not (ENABLE_PHASE3_NAVIGATION and USE_DWA):
        return None
    
    if not swarm.dwa_planners:
        return None
    
    # Aggregate DWA planner state (smoothness level)
    total_smoothing = sum(p.last_heading for p in swarm.dwa_planners)
    avg_smoothing = total_smoothing / len(swarm.dwa_planners) if swarm.dwa_planners else 0
    
    # Count robots with significant velocity (actively planning)
    active_robots = 0
    velocities = swarm.get_robot_velocities()
    for vx, vy in velocities:
        if np.sqrt(vx**2 + vy**2) > 0.1:
            active_robots += 1
    
    return {
        'dwa_planners_active': len(swarm.dwa_planners),
        'prediction_steps': DWA_PREDICTION_STEPS,
        'actively_navigating_robots': active_robots,
        'avg_heading_angle': avg_smoothing,
    }


def get_phase4_stats(environment):
    """
    Calculate Phase 4 environment complexity metrics.
    
    Returns:
        Dictionary with terrain and dynamic obstacle statistics
    """
    stats = {}
    
    # Terrain system metrics
    if environment.terrain_system is not None:
        terrain_stats = environment.terrain_system.get_statistics()
        stats['terrain_zones'] = terrain_stats['total_zones']
        stats['friction_zones'] = terrain_stats['friction_zones']
        stats['slippy_zones'] = terrain_stats['slippy_zones']
    else:
        stats['terrain_zones'] = 0
        stats['friction_zones'] = 0
        stats['slippy_zones'] = 0
    
    # Dynamic obstacles metrics
    if environment.dynamic_obstacles is not None:
        active_obstacles = len(environment.dynamic_obstacles.obstacles)
        stats['active_obstacles'] = active_obstacles
        stats['total_spawned'] = environment.dynamic_obstacles.next_id
    else:
        stats['active_obstacles'] = 0
        stats['total_spawned'] = 0
    
    return stats


def generate_unique_filename(base_name: str = "swarm_simulation") -> str:
    """
    Generate a unique filename with timestamp.
    
    Args:
        base_name: Base filename without extension
        
    Returns:
        Filename with timestamp: base_name_YYYY-MM-DD_HHMMSS
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return f"{base_name}_{timestamp}"


def save_animation_video(output_file=None, fps=20, save_mp4=True):
    """
    Save swarm simulation as video file with unique timestamped filename.
    
    Args:
        output_file: Output filename (without extension). If None, generates unique timestamp-based name
        fps: Frames per second
        save_mp4: Also try to save as MP4 (requires ffmpeg)
    """
    
    # Generate unique filename if not provided
    if output_file is None:
        output_file = generate_unique_filename("swarm_simulation")
    
    print("=" * 70)
    print("SWARM ROBOTICS - VIDEO SAVING MODE WITH PHASE 1 & 2 & 3 METRICS")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Environment: {ENVIRONMENT_WIDTH}x{ENVIRONMENT_HEIGHT}")
    print(f"  Number of Robots: {NUM_ROBOTS}")
    print(f"  Number of Obstacles: {NUM_OBSTACLES}")
    print(f"  Target Position: ({TARGET_X}, {TARGET_Y})")
    print(f"\nVideo Settings:")
    print(f"  FPS: {fps}")
    print(f"  Output GIF: outputs/animations/{output_file}.gif")
    if save_mp4:
        print(f"  Output MP4: outputs/videos/{output_file}.mp4")
    print()
    
    # Create environment and swarm
    print("Initializing simulation...")
    environment = create_environment()
    swarm = RobotSwarm(NUM_ROBOTS, environment, ROBOT_SPEED, ROBOT_SENSOR_RANGE)
    print(f"✓ Environment ready with {len(environment.obstacles)} obstacles")
    print(f"✓ Swarm initialized with {NUM_ROBOTS} robots\n")
    
    # Setup figure
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, ENVIRONMENT_WIDTH)
    ax.set_ylim(0, ENVIRONMENT_HEIGHT)
    ax.set_aspect('equal')
    ax.set_title('Swarm Robotics - Phase 1, 2 & 3 (DWA Navigation)', 
                fontsize=14, fontweight='bold')
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
                       fontsize=8, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85),
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
            f"[PHASE 1] [PHASE 2] [PHASE 3 DWA]\n"
            f"Iteration: {step_data['iteration']:3d}  |  "
            f"Fitness: {step_data['best_fitness']:7.2f}  |  "
            f"Coverage: {step_data['exploration_coverage']:5.1f}%  |  "
            f"Near Target: {step_data['robots_near_target']:2d}/{NUM_ROBOTS}\n"
            f"Speed: {step_data['avg_robot_speed']:5.2f}  |  "
            f"Spread: {swarm.get_swarm_spread():5.2f}  |  "
            f"Position: ({center_x:6.1f}, {center_y:6.1f})"
        )
        
        # Add Phase 2 metrics if enabled
        if ENABLE_PHASE2_INTERACTION:
            phase2_stats = get_phase2_stats(swarm)
            if phase2_stats:
                info_str += f"\n[PHASE 2: INTERACTIONS] "
                info_str += f"Spacing: {phase2_stats['min_spacing']:.2f}u | "
                if phase2_stats['active_collision']:
                    info_str += f"⚠ COLLISION | "
                info_str += f"Comm: {phase2_stats['communication_pairs']} pairs"
        
        # Add Phase 3 metrics if enabled
        if ENABLE_PHASE3_NAVIGATION and USE_DWA:
            phase3_stats = get_phase3_stats(swarm)
            if phase3_stats:
                info_str += f"\n[PHASE 3: DWA] "
                info_str += f"Planners: {phase3_stats['dwa_planners_active']} | "
                info_str += f"Active: {phase3_stats['actively_navigating_robots']}/{NUM_ROBOTS} | "
                info_str += f"Prediction: {phase3_stats['prediction_steps']} steps"
        
        # Add Phase 4 metrics if enabled
        if swarm.environment.phase4_enabled:
            phase4_stats = get_phase4_stats(swarm.environment)
            if phase4_stats:
                info_str += f"\n[PHASE 4: ENVIRONMENT] "
                info_str += f"Terrain: {phase4_stats['terrain_zones']} zones "
                info_str += f"({phase4_stats['friction_zones']}F/{phase4_stats['slippy_zones']}S) | "
                info_str += f"Obstacles: {phase4_stats['active_obstacles']}/{phase4_stats['total_spawned']}"
        
        
        if step_data['target_found']:
            info_str += "\n\n✓ TARGET FOUND!"
            ax.set_title('✓ TARGET FOUND! - Swarm Robotics Path Planning and Exploration', 
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
    
    # Ensure output directories exist
    os.makedirs("outputs/animations", exist_ok=True)
    os.makedirs("outputs/videos", exist_ok=True)
    
    # Save as GIF
    print("\n" + "=" * 70)
    print("SAVING ANIMATION...")
    print("=" * 70)
    
    gif_file = f"outputs/animations/{output_file}.gif"
    print(f"\nSaving GIF: outputs/animations/{output_file}.gif")
    print("(This may take a few minutes for smooth animation...)")
    
    try:
        anim.save(gif_file, writer='pillow', fps=fps, dpi=80)
        print(f"✓ GIF saved successfully!")
        print(f"  File size: {os.path.getsize(gif_file) / (1024*1024):.1f} MB")
    except Exception as e:
        print(f"✗ Failed to save GIF: {e}")
    
    # Try to save as MP4 if ffmpeg available
    if save_mp4:
        mp4_file = f"outputs/videos/{output_file}.mp4"
        print(f"\nSaving MP4: outputs/videos/{output_file}.mp4")
        try:
            anim.save(mp4_file, writer='ffmpeg', fps=fps, dpi=80)
            print(f"✓ MP4 saved successfully!")
            print(f"  File size: {os.path.getsize(mp4_file) / (1024*1024):.1f} MB")
        except Exception as e:
            print(f"✗ MP4 not saved (ffmpeg may not be installed)")
            print(f"  Error: {e}")
    
    plt.close(fig)
    
    # Print results
    if state['final_data']:
        final = state['final_data']
        print("\n" + "=" * 70)
        print("SIMULATION RESULTS")
        print("=" * 70)
        print(f"Total Iterations: {state['iteration']}")
        print(f"Target Found: {'YES ✓' if state['target_found'] else 'NO'}")
        print(f"Final Exploration Coverage: {final['exploration_coverage']:.1f}%")
        print(f"Best Fitness Achieved: {final['best_fitness']:.2f}")
        print(f"Robots Near Target: {final['robots_near_target']}/{NUM_ROBOTS}")
        print(f"Swarm Spread: {swarm.get_swarm_spread():.2f}")
        print("=" * 70)
        
        print(f"\n✓ Video saved! You can find it in the outputs folder:")
        print(f"  📁 GIF:  outputs/animations/{output_file}.gif")
        if save_mp4:
            print(f"  📁 MP4:  outputs/videos/{output_file}.mp4")


if __name__ == "__main__":
    save_animation_video(
        fps=10,  # 10 FPS for smooth video
        save_mp4=True  # Try to save MP4 as well
        # output_file will be auto-generated with timestamp
    )

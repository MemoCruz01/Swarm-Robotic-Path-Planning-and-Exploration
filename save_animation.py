"""
Save swarm robotics simulation as video file (MP4 and GIF).
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import os

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


def save_animation_video(output_file="swarm_simulation.gif", fps=20, save_mp4=True):
    """
    Save swarm simulation as video file.
    
    Args:
        output_file: Output filename (without extension for multiple formats)
        fps: Frames per second
        save_mp4: Also try to save as MP4 (requires ffmpeg)
    """
    
    print("=" * 70)
    print("SWARM ROBOTICS - VIDEO SAVING MODE")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Environment: {ENVIRONMENT_WIDTH}x{ENVIRONMENT_HEIGHT}")
    print(f"  Number of Robots: {NUM_ROBOTS}")
    print(f"  Number of Obstacles: {NUM_OBSTACLES}")
    print(f"  Target Position: ({TARGET_X}, {TARGET_Y})")
    print(f"\nVideo Settings:")
    print(f"  FPS: {fps}")
    print(f"  Output: {output_file}.gif")
    if save_mp4:
        print(f"  Also attempting: {output_file}.mp4")
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
    ax.set_title('Swarm Robotics - Path Planning and Exploration', 
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
        
        if step_data['target_found']:
            info_str += "  |  ✓ TARGET FOUND!"
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
    
    # Save as GIF
    print("\n" + "=" * 70)
    print("SAVING ANIMATION...")
    print("=" * 70)
    
    gif_file = f"{output_file}.gif"
    print(f"\nSaving GIF: {gif_file}")
    print("(This may take a few minutes for smooth animation...)")
    
    try:
        anim.save(gif_file, writer='pillow', fps=fps, dpi=80)
        print(f"✓ GIF saved successfully: {gif_file}")
        print(f"  File size: {os.path.getsize(gif_file) / (1024*1024):.1f} MB")
    except Exception as e:
        print(f"✗ Failed to save GIF: {e}")
    
    # Try to save as MP4 if ffmpeg available
    if save_mp4:
        mp4_file = f"{output_file}.mp4"
        print(f"\nSaving MP4: {mp4_file}")
        try:
            anim.save(mp4_file, writer='ffmpeg', fps=fps, dpi=80)
            print(f"✓ MP4 saved successfully: {mp4_file}")
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
        
        print(f"\n✓ Video saved! You can find it in the project directory:")
        print(f"  {os.path.abspath(gif_file)}")
        if save_mp4:
            print(f"  {os.path.abspath(mp4_file)}")


if __name__ == "__main__":
    save_animation_video(
        output_file="swarm_simulation",
        fps=10,  # 10 FPS for smooth video
        save_mp4=True  # Try to save MP4 as well
    )

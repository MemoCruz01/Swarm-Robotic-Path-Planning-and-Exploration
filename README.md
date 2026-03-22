# Swarm Robotics: Path Planning and Exploration

A Python simulation of swarm robotics using Particle Swarm Optimization (PSO) for autonomous exploration and path planning.

## Features

- **PSO Algorithm**: Implements Particle Swarm Optimization adapted for multi-robot systems
- **Swarm Exploration**: 15 robots working collectively to explore an environment
- **Obstacle Avoidance**: Dynamic obstacle avoidance during navigation
- **Real-time Visualization**: Animated visualization of robot movement and swarm behavior
- **Convergence Analysis**: Tracking of fitness metrics, exploration coverage, and performance

## Project Structure

```
├── main.py                 # Main simulation entry point
├── requirements.txt        # Python dependencies
├── config/
│   └── settings.py        # Configuration parameters
└── src/
    ├── __init__.py
    ├── environment.py     # Environment and obstacle definitions
    ├── robot.py          # Individual robot agent class
    ├── swarm.py          # Swarm management and coordination
    ├── pso.py            # PSO algorithm implementation
    └── visualization.py   # Matplotlib visualization and animation
```

## Configuration

Edit `config/settings.py` to customize:

- **Environment Size**: `ENVIRONMENT_WIDTH`, `ENVIRONMENT_HEIGHT`
- **Number of Robots**: `NUM_ROBOTS`
- **PSO Parameters**: `PSO_W`, `PSO_C1`, `PSO_C2`
- **Target Position**: `TARGET_X`, `TARGET_Y`
- **Number of Obstacles**: `NUM_OBSTACLES`
- **Visualization**: `ANIMATION_SPEED`, `SHOW_VELOCITY_VECTORS`

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the simulation:
```bash
python main.py
```

## How It Works

### Particle Swarm Optimization (PSO)

The algorithm uses PSO to guide the swarm toward the target while exploring the environment:

1. **Fitness Function**: Combines distance-to-target and exploration rewards
2. **Velocity Update**: Each robot adjusts velocity based on:
   - Its own best position
   - Swarm's global best position
   - Inertia weight for convergence control

3. **Position Update**: Robots move based on updated velocities
4. **Obstacle Avoidance**: Automatic repulsion from nearby obstacles
5. **Boundary Constraints**: Robots bounce off environment edges

### Real-World Applications

- **Disaster Recovery**: Autonomous drones searching collapsed buildings
- **Environmental Monitoring**: Swarms exploring forests or underwater environments
- **Mine Detection**: Coordinated robots sweeping areas for explosive devices
- **Search & Rescue**: Multiple agents locating survivors in unknown terrain

## Visualization

The simulation displays:

- **Blue Circles**: Robot positions
- **Gray Circles**: Obstacles
- **Red Circle**: Target location
- **Blue Star**: Swarm center of mass
- **Right Panel**: Real-time statistics (fitness, exploration, speed)

### Convergence Plots

After simulation, the tool shows:
- **Best Fitness**: How well the algorithm is performing
- **Exploration Coverage**: Percentage of environment discovered
- **Robots Near Target**: Count of robots approaching target
- **Average Speed**: Swarm velocity dynamics

## Customization

### Modify PSO Parameters

In `config/settings.py`:
```python
PSO_W = 0.7298      # Inertia weight (0.4-0.9 typical)
PSO_C1 = 1.49618    # Cognitive parameter
PSO_C2 = 1.49618    # Social parameter
```

### Change Environment

Edit the `create_environment()` function in `main.py` to add custom obstacles or use different configurations.

### Implement Different Fitness Functions

Modify the `fitness_function()` method in `src/pso.py` to prioritize different objectives (exploration vs. target-reaching).

## Performance Tips

- Increase `PSO_W` for faster convergence (but risk overshooting)
- Increase robot count (`NUM_ROBOTS`) for better exploration
- Adjust `ROBOT_SENSOR_RANGE` for more/less obstacle awareness
- Use `SHOW_VELOCITY_VECTORS=False` for cleaner visualization

## License

Educational use - Swarm Robotics Research Project

## References

- Kennedy, J., & Eberhart, R. (1995). "Particle swarm optimization"
- Dorigo, M., & Stützle, T. (2019). "Ant Colony Optimization"
- Hüttenrauch, M., et al. (2019). "Deep Reinforcement Learning for Swarm Systems"

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
├── scripts/                # All simulation scripts
│   ├── main.py            # Full simulation with GUI visualization
│   ├── animate_swarm.py   # Live animation of swarm movement
│   ├── save_animation.py  # Save simulation as video (GIF/MP4)
│   └── test_simulation.py # Quick test without GUI
├── batch_files/           # Easy execution scripts (for Windows)
│   ├── run_animation.bat
│   ├── save_video.bat
│   ├── quick_test.bat
│   └── run_main.bat
├── outputs/              # Simulation outputs
│   ├── animations/       # Saved GIF animations
│   ├── videos/          # Saved MP4 videos
│   ├── logs/            # Simulation logs
│   └── data/            # Simulation data/metrics
├── docs/                # Documentation files
├── config/
│   └── settings.py      # Configuration parameters
└── src/
    ├── __init__.py
    ├── environment.py   # Environment and obstacle definitions
    ├── robot.py        # Individual robot agent class
    ├── swarm.py        # Swarm management and coordination
    ├── pso.py          # PSO algorithm implementation
    └── visualization.py # Matplotlib visualization and animation
```

## Quick Start

### Run a Quick Test (No GUI - 2 seconds)
```bash
python scripts/test_simulation.py
```

### Run Full Simulation with Visualization
```bash
python scripts/main.py
```

### Watch Live Animation
```bash
python scripts/animate_swarm.py
```

### Save Simulation as Video
```bash
python scripts/save_animation.py
# Outputs to: outputs/videos/swarm_simulation.gif
```

### Easy Windows Execution
Double-click any `.bat` file in the `batch_files/` folder:
- `run_animation.bat` - Live animation
- `save_video.bat` - Save as GIF/MP4
- `quick_test.bat` - Quick 200-iteration test
- `run_main.bat` - Full simulation with graphs

## Configuration

Edit `config/settings.py` to customize:

- **Environment Size**: `ENVIRONMENT_WIDTH`, `ENVIRONMENT_HEIGHT`
- **Number of Robots**: `NUM_ROBOTS`
- **PSO Parameters**: `PSO_W`, `PSO_C1`, `PSO_C2`
- **Target Position**: `TARGET_X`, `TARGET_Y`
- **Number of Obstacles**: `NUM_OBSTACLES`
- **Visualization**: `ANIMATION_SPEED`, `SHOW_VELOCITY_VECTORS`
- **Stopping Conditions**: See `docs/STOPPING_CONDITIONS.md`

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

## Output Directory Structure

```
outputs/
├── animations/          # GIF animations from save_animation.py
├── videos/             # MP4 videos (requires ffmpeg)
├── logs/               # Simulation execution logs
└── data/               # CSV/JSON simulation metrics
```

## Customization

### Modify PSO Parameters

In `config/settings.py`:
```python
PSO_W = 0.7298      # Inertia weight (0.4-0.9 typical)
PSO_C1 = 1.49618    # Cognitive parameter
PSO_C2 = 1.49618    # Social parameter
```

### Change Environment

Edit `scripts/main.py` in the `create_environment()` function to add custom obstacles.

### Implement Different Fitness Functions

Modify `fitness_function()` in `src/pso.py` to prioritize different objectives.

### Control Stopping Conditions

Edit `config/settings.py` and set:
```python
STOP_ON_SINGLE_ROBOT = False      # Stop when first robot reaches target
STOP_ON_ALL_ROBOTS = False        # Stop when all robots reach target
STOP_ON_PERCENTAGE = True         # Stop when X% reach target
TARGET_ROBOT_PERCENTAGE = 80      # Stop at 80% (12/15 robots)
```

See `docs/STOPPING_CONDITIONS.md` for detailed explanation.

## Performance Tips

- Increase `PSO_W` for faster convergence (but risk overshooting)
- Increase robot count (`NUM_ROBOTS`) for better exploration
- Adjust `ROBOT_SENSOR_RANGE` for more/less obstacle awareness
- Use `SHOW_VELOCITY_VECTORS=False` for cleaner visualization
- Use `scripts/test_simulation.py` for fast algorithm testing
- Use `scripts/animate_swarm.py` for interactive visualization

## Troubleshooting

**"ModuleNotFoundError"**:
```bash
pip install -r requirements.txt
```

**On Linux (no display)**:
Use `scripts/test_simulation.py` instead (no GUI required)

**Simulation too fast**:
Increase `VISUALIZATION_INTERVAL` in `config/settings.py`

**MP4 not saving**:
Install ffmpeg: `pip install ffmpeg` (GIF will still work)

## Documentation Files

- **README.md** (this file) - Project overview
- **docs/QUICK_START.md** - Getting started guide
- **docs/PROJECT_SETUP.md** - Project structure details
- **docs/STOPPING_CONDITIONS.md** - Configuration guide for stopping conditions

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. On Windows, double-click a `.bat` file from `batch_files/` folder

3. On Linux/Mac, run:
```bash
python scripts/main.py
```

## License

Educational use - Swarm Robotics Research Project

## References

- Kennedy, J., & Eberhart, R. (1995). "Particle swarm optimization"
- Dorigo, M., & Stützle, T. (2019). "Ant Colony Optimization"
- Hüttenrauch, M., et al. (2019). "Deep Reinforcement Learning for Swarm Systems"

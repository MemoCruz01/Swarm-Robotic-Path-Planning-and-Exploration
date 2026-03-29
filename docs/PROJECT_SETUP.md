# Project Setup Summary

## ✓ Project Successfully Created and Tested

### Test Results
- **Target Found**: Yes ✓
- **Iterations to Find Target**: 10 iterations
- **Robots Near Target**: 4 out of 15 robots
- **Best Fitness**: -5.18
- **Exploration Coverage**: 5.0%

---

## Project Structure

```
Swarm Robotic Path Planning and Exploration/
├── scripts/                  # All simulation and test scripts
│   ├── main.py             # Full simulation with visualization
│   ├── animate_swarm.py    # Live animation viewer
│   ├── save_animation.py   # Save as GIF/MP4
│   └── test_simulation.py  # Quick test without GUI
├── batch_files/            # Windows batch files for easy execution
│   ├── run_animation.bat
│   ├── save_video.bat
│   ├── quick_test.bat
│   └── run_main.bat
├── outputs/                # All output files go here
│   ├── animations/        # Saved GIF animations
│   ├── videos/           # Saved MP4 videos
│   ├── logs/             # Simulation logs
│   └── data/             # Simulation data/metrics
├── docs/                  # Documentation files
│   ├── README.md
│   ├── QUICK_START.md
│   ├── PROJECT_SETUP.md
│   └── STOPPING_CONDITIONS.md
├── config/
│   └── settings.py       # All configuration parameters
└── src/
    ├── __init__.py
    ├── environment.py    # Environment and obstacle classes
    ├── robot.py          # Individual robot agent class
    ├── swarm.py          # Swarm management and coordination
    ├── pso.py            # PSO algorithm implementation
    └── visualization.py  # Matplotlib visualization
```

---

## Core Components

### 1. **Environment Module** (`src/environment.py`)
- Obstacle class for circular obstacles
- Environment class managing boundaries and collisions
- Exploration tracking system
- Target location and distance calculations

### 2. **Robot Module** (`src/robot.py`)
- Individual robot agents with position and velocity
- PSO velocity update mechanism
- Obstacle avoidance logic
- Personal best position tracking

### 3. **PSO Algorithm** (`src/pso.py`)
- Particle Swarm Optimization implementation
- Fitness function combining target-reaching and exploration objectives
- Global best position tracking
- Convergence metrics

### 4. **Swarm Management** (`src/swarm.py`)
- RobotSwarm class coordinating multiple robots
- Statistics tracking (fitness, coverage, speed)
- Swarm center and spread calculations
- Simulation stepping

### 5. **Visualization** (`src/visualization.py`)
- Real-time animated visualization
- Static frame display
- Convergence metrics plots
- Animation saving capability

---

## How to Run

### Method 1: Windows - Double-click batch files
Double-click any file in `batch_files/` folder:
- `quick_test.bat` - Fastest test (200 iterations, no GUI)
- `run_animation.bat` - Watch robots explore
- `save_video.bat` - Save simulation as GIF
- `run_main.bat` - Full simulation with graphs

### Method 2: Command Line
```bash
# Quick test (5-10 seconds)
python scripts/test_simulation.py

# Live animation (interactive, 20-30 seconds)
python scripts/animate_swarm.py

# Save as video (60-90 seconds, creates outputs/videos/swarm_simulation.gif)
python scripts/save_animation.py

# Full simulation with analysis (30-45 seconds)
python scripts/main.py
```

---

## Configuration

Edit `config/settings.py` to customize:

### Swarm Settings
```python
NUM_ROBOTS = 15              # Number of robots
ROBOT_SPEED = 2.0           # Speed per iteration
ROBOT_SENSOR_RANGE = 15.0   # Obstacle detection range
```

### Environment Settings
```python
ENVIRONMENT_WIDTH = 100
ENVIRONMENT_HEIGHT = 100
NUM_OBSTACLES = 8
TARGET_X = 80
TARGET_Y = 80
```

### PSO Parameters
```python
PSO_W = 0.7298      # Inertia weight
PSO_C1 = 1.49618    # Cognitive parameter
PSO_C2 = 1.49618    # Social parameter
PSO_ITERATIONS = 500
```

### Visualization Settings
```python
ANIMATION_SPEED = 50        # Milliseconds between frames
SHOW_VELOCITY_VECTORS = True
VISUALIZATION_INTERVAL = 10 # Print progress every N iterations
```

---

## Algorithm Features

### Particle Swarm Optimization
1. **Fitness Evaluation**: Combines distance to target + exploration bonus
2. **Velocity Update**: PSO equation with inertia and social components
3. **Position Update**: Moves robots based on velocity
4. **Obstacle Avoidance**: Repulsion force from nearby obstacles
5. **Boundary Enforcement**: Bouncing when hitting environment edges
6. **Exploration Tracking**: Records visited regions

### Collision Avoidance (3-Level System)
1. **Predictive Detection**: Looks ahead 3.0 units for obstacles
2. **Dynamic Repulsion**: Force 0.5-3.0 based on proximity
3. **Position Correction**: Push out and bounce if collision occurs

### Real-World Applications
- **Disaster Recovery**: Autonomous drones in collapsed buildings
- **Environmental Monitoring**: Forest and underwater exploration
- **Mine Detection**: Coordinated sweeping operations
- **Search & Rescue**: Finding survivors in unknown terrain
- **Area Coverage**: Efficient coverage of large zones
- **Perimeter Surveillance**: Monitoring boundaries

---

## Visualization Output

The main GUI displays:
- **Blue circles**: Robot positions
- **Gray circles**: Obstacles
- **Red circle**: Target location
- **Blue star**: Swarm center of mass
- **Cyan vectors**: Velocity directions (optional)

### Right Panel Statistics
- Iteration count
- Best fitness value
- Exploration coverage percentage
- Robots near target count
- Average swarm speed
- Swarm spread (cohesion metric)
- Global best position

### Convergence Plots
- Best fitness over iterations
- Exploration coverage progression
- Robots approaching target
- Average swarm velocity dynamics

---

## Performance Metrics

The simulation tracks and displays:
1. **Fitness Progression**: How well the algorithm is optimizing
2. **Exploration Coverage**: Percentage of environment explored
3. **Convergence Speed**: Iterations to reach target
4. **Swarm Cohesion**: Distance spread of robot swarm
5. **Robot Coordination**: Number of robots near objective

---

## Customization Examples

### Increase Swarm Size
```python
# config/settings.py
NUM_ROBOTS = 30  # Larger swarm for better coverage
```

### Modify PSO Behavior
```python
# config/settings.py
PSO_W = 0.5      # Lower inertia = faster convergence
PSO_C1 = 2.0     # Higher cognitive = more individual exploration
PSO_C2 = 2.0     # Higher social = more collective behavior
```

### Change Environment Complexity
```python
# config/settings.py
NUM_OBSTACLES = 15      # More challenging environment
OBSTACLE_MAX_SIZE = 12  # Larger obstacles
ENVIRONMENT_WIDTH = 150 # Larger space to explore
```

### Control When to Stop
See `docs/STOPPING_CONDITIONS.md` for options:
```python
# Stop when first robot finds target
STOP_ON_SINGLE_ROBOT = True

# Stop when all robots find target
STOP_ON_ALL_ROBOTS = False

# Stop when 80% of robots find target (RECOMMENDED)
STOP_ON_PERCENTAGE = True
TARGET_ROBOT_PERCENTAGE = 80
```

---

## Output Locations

```
outputs/
├── animations/              # GIF files from save_animation.py
│   └── swarm_simulation.gif
├── videos/                 # MP4 files (requires ffmpeg)
│   └── swarm_simulation.mp4
├── logs/                   # Simulation execution logs
│   └── simulation_2024-03-26.log
└── data/                   # Simulation metrics (CSV/JSON)
    └── metrics.csv
```

---

## Next Steps

1. **Run Simulations**: Double-click a `.bat` file or run `python scripts/test_simulation.py`
2. **Analyze Results**: Study convergence metrics and robot behavior
3. **Experiment**: Modify `config/settings.py` and observe effects
4. **Extend**: Implement additional features:
   - Multi-target exploration
   - Dynamic obstacles
   - Energy/fuel constraints
   - Formation control
   - Cooperative communication network

---

## Dependencies

- **NumPy** (2.4.3): Numerical computations
- **Matplotlib** (3.10.8): Visualization and animation
- **SciPy** (1.17.1): Scientific computing utilities
- **Python** (3.11.9): Runtime environment

Install with:
```bash
pip install -r requirements.txt
```

---

## Performance Tips for Large Simulations

1. Use `scripts/test_simulation.py` for algorithm testing (no GUI overhead)
2. Disable `SHOW_VELOCITY_VECTORS = False` for faster rendering
3. Increase `VISUALIZATION_INTERVAL` to reduce console output
4. Use `ANIMATION_SPEED = 100` for faster visualization
5. Reduce `NUM_ROBOTS` for quicker simulations during development

---

## File Organization Guidelines

When creating new simulations or experiments:

1. **Save outputs to `outputs/` directory**:
   - GIFs → `outputs/animations/`
   - Videos → `outputs/videos/`
   - Logs → `outputs/logs/`
   - Data → `outputs/data/`

2. **Keep scripts in `scripts/` directory**
3. **Keep batch files in `batch_files/`**
4. **Keep configuration in `config/settings.py`**
5. **Keep core modules in `src/`**

This maintains clean organization for future simulations and experiments.

---

## Troubleshooting

**"ModuleNotFoundError"**: 
Run `pip install -r requirements.txt`

**On Linux (no display)**: 
Use `python scripts/test_simulation.py`

**Simulation too fast**: 
Increase `ANIMATION_SPEED` in `config/settings.py`

**MP4 not saving**: 
GIF will still work. Install ffmpeg for MP4: `pip install ffmpeg`

**Robots pass through obstacles**: 
Check `MIN_OBSTACLE_DISTANCE` in `config/settings.py` (should be ≥ 8.0)

---

## Documentation Files

- **docs/README.md** - Project overview and features
- **docs/QUICK_START.md** - Getting started guide
- **docs/PROJECT_SETUP.md** - This file, project structure details
- **docs/STOPPING_CONDITIONS.md** - Configuration for stop conditions

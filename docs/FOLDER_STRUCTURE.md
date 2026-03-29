# 📁 Folder Organization Guide

## Project Directory Structure

```
Swarm Robotic Path Planning and Exploration/
│
├── 📂 scripts/                          # All executable simulation scripts
│   ├── main.py                         # Full simulation with GUI & analysis
│   ├── animate_swarm.py                # Live animation viewer
│   ├── save_animation.py               # Save simulation as GIF/MP4
│   └── test_simulation.py              # Quick test (no GUI, 5 seconds)
│
├── 📂 batch_files/                      # Windows batch files (double-click to run)
│   ├── run_animation.bat               # Launch live animation
│   ├── save_video.bat                  # Save simulation as video
│   ├── quick_test.bat                  # Run 200-iteration test
│   └── run_main.bat                    # Full simulation with graphs
│
├── 📂 outputs/                          # ALL simulation outputs go here
│   ├── animations/                     # Saved GIF animations
│   │   └── swarm_simulation.gif        # Latest animation output
│   ├── videos/                         # Saved MP4 videos (requires ffmpeg)
│   │   └── swarm_simulation.mp4        # Latest video output
│   ├── logs/                           # Simulation execution logs
│   │   └── simulation_*.log            # Timestamped logs
│   └── data/                           # Simulation metrics & data
│       └── metrics.csv                 # CSV export of simulation data
│
├── 📂 docs/                             # Documentation files
│   ├── README.md                       # Overview & main documentation
│   ├── QUICK_START.md                  # Getting started guide
│   ├── PROJECT_SETUP.md                # Project structure & details
│   ├── STOPPING_CONDITIONS.md          # Configuration for stop conditions
│   └── FOLDER_STRUCTURE.md             # This file (folder organization)
│
├── 📂 config/                           # Configuration files
│   └── settings.py                     # All simulation parameters
│
├── 📂 src/                              # Core source code modules
│   ├── __init__.py
│   ├── environment.py                  # Environment & obstacle management
│   ├── robot.py                        # Individual robot agent class
│   ├── swarm.py                        # Swarm coordination & stepping
│   ├── pso.py                          # PSO algorithm implementation
│   └── visualization.py                # Matplotlib visualization
│
├── 📂 .git/                             # Git version control
├── .gitignore                           # Git ignore patterns
├── requirements.txt                    # Python dependencies
└── README.md                            # Root-level README (could link to docs/)

```

---

## 📖 What Goes Where?

### ✅ `scripts/` - All Executable Code
**Purpose**: Entry points for running simulations
**Files**:
- `main.py` - Full simulation with visualization and analysis
- `animate_swarm.py` - Interactive animation viewer
- `save_animation.py` - Render and save videos
- `test_simulation.py` - Quick algorithm testing

**When to use**:
- Run `main.py` for detailed analysis with graphs
- Run `animate_swarm.py` to watch robots interactively
- Run `save_animation.py` to create GIF/MP4 videos
- Run `test_simulation.py` for fast testing (no GUI)

---

### ✅ `batch_files/` - Windows Batch Scripts
**Purpose**: Easy execution without typing commands
**Files**:
- `run_animation.bat` - Calls `scripts/animate_swarm.py`
- `save_video.bat` - Calls `scripts/save_animation.py`
- `quick_test.bat` - Calls `scripts/test_simulation.py`
- `run_main.bat` - Calls `scripts/main.py`

**When to use**:
- **Windows users**: Double-click any `.bat` file
- **Command line users**: Run `python scripts/main.py` directly

**For Linux/Mac**:
Use the command line examples in the respective `.bat` files

---

### ✅ `outputs/` - All Simulation Results
**Purpose**: Centralized location for all generated files
**Subfolders**:

#### `outputs/animations/`
- **Contains**: GIF files from `save_animation.py`
- **File naming**: `swarm_simulation_TIMESTAMP.gif`
- **Purpose**: Shareable animation videos
- **Size**: ~5-50 MB depending on simulation length

#### `outputs/videos/`
- **Contains**: MP4 videos (requires ffmpeg)
- **File naming**: `swarm_simulation_TIMESTAMP.mp4`
- **Purpose**: High-quality video exports
- **Size**: ~20-100 MB depending on video length

#### `outputs/logs/`
- **Contains**: Simulation execution logs
- **File naming**: `simulation_2024-03-26_14-30-45.log`
- **Purpose**: Debugging and performance tracking
- **Format**: Text files with timestamp and metrics

#### `outputs/data/`
- **Contains**: Exported simulation metrics
- **File naming**: `metrics_TIMESTAMP.csv`
- **Purpose**: Data analysis and plotting
- **Format**: CSV with fitness, coverage, speed metrics

**Organization Benefit**:
- Keeps root directory clean
- All outputs in one location
- Easy to backup or share results
- Can delete old simulations without affecting code

---

### ✅ `docs/` - Documentation Files
**Purpose**: Comprehensive project documentation
**Files**:

| File | Purpose | Audience |
|------|---------|----------|
| `README.md` | Project overview & features | Everyone |
| `QUICK_START.md` | Getting started in 2 minutes | Beginners |
| `PROJECT_SETUP.md` | Complete structure details | Developers |
| `STOPPING_CONDITIONS.md` | Configuration guide | Users |
| `FOLDER_STRUCTURE.md` | This file | Organization reference |

**Best Practices**:
- Read `QUICK_START.md` first
- Check `STOPPING_CONDITIONS.md` before configuring
- Reference `PROJECT_SETUP.md` for custom modifications

---

### ✅ `config/` - Configuration Files
**Purpose**: Centralized parameter management
**Files**:
- `settings.py` - All tunable parameters

**Customizable Parameters**:
```python
# Swarm settings
NUM_ROBOTS = 15
ROBOT_SPEED = 2.0
ROBOT_SENSOR_RANGE = 15.0

# Environment settings
ENVIRONMENT_WIDTH = 100
ENVIRONMENT_HEIGHT = 100
NUM_OBSTACLES = 8
TARGET_X = 80
TARGET_Y = 80

# PSO parameters
PSO_W = 0.7298
PSO_C1 = 1.49618
PSO_C2 = 1.49618
PSO_ITERATIONS = 500

# Stopping conditions
STOP_ON_SINGLE_ROBOT = False
STOP_ON_ALL_ROBOTS = False
STOP_ON_PERCENTAGE = True
TARGET_ROBOT_PERCENTAGE = 80
```

**Benefits**:
- Single file to modify for all experiments
- No need to edit core code
- Easy version control of configurations
- Shareable parameter sets

---

### ✅ `src/` - Core Source Code
**Purpose**: Core algorithms and components
**Files**:

| Module | Purpose |
|--------|---------|
| `environment.py` | World, obstacles, targets, collision detection |
| `robot.py` | Individual robot agent, PSO updates, avoidance |
| `swarm.py` | Multi-robot coordination, statistics |
| `pso.py` | Particle Swarm Optimization algorithm |
| `visualization.py` | Plotting and animation rendering |

**Organization**:
- Each class/concept in its own file
- Clear dependencies between modules
- Easy to extend or modify individual components

---

## 🎯 Workflow: Creating a New Simulation

### Step 1: Modify Configuration
```
Edit: config/settings.py
- Change NUM_ROBOTS, NUM_OBSTACLES, TARGET, etc.
- Set stopping conditions
```

### Step 2: Run Simulation
```
Choose one:
- python scripts/test_simulation.py      (5 seconds, no GUI)
- python scripts/animate_swarm.py        (30 seconds, interactive)
- python scripts/save_animation.py       (90 seconds, saves GIF)
- python scripts/main.py                 (45 seconds, full analysis)
```

### Step 3: View Results
```
Check outputs/:
- outputs/animations/swarm_simulation.gif    (video)
- outputs/videos/swarm_simulation.mp4        (larger video)
- outputs/logs/simulation_*.log              (metrics)
- outputs/data/metrics.csv                   (data export)
```

### Step 4: Analyze Results
```
Review plots and statistics:
- Fitness convergence
- Exploration coverage
- Robot approach to target
- Swarm velocity dynamics
```

---

## 📊 File Size Reference

```
Typical File Sizes:
├── scripts/
│   ├── main.py                      ~15 KB
│   ├── animate_swarm.py            ~12 KB
│   ├── save_animation.py           ~14 KB
│   └── test_simulation.py          ~8 KB
│
├── outputs/
│   ├── animations/swarm_*.gif      5-50 MB    (depends on length)
│   ├── videos/swarm_*.mp4         20-100 MB   (High quality)
│   ├── logs/simulation_*.log        1-10 KB    (Metrics only)
│   └── data/metrics.csv             5-50 KB    (Raw data)
│
└── src/
    ├── environment.py              ~8 KB
    ├── robot.py                   ~12 KB
    ├── swarm.py                   ~16 KB
    ├── pso.py                      ~9 KB
    └── visualization.py           ~18 KB
```

---

## 🔄 Growth Strategy for Future Experiments

### Adding New Features
```
Create files in src/:
src/
├── environment.py        (modify for new features)
├── robot.py             (modify for new robot behavior)
├── communication.py     (NEW - for message passing)
├── energy.py           (NEW - for fuel constraints)
├── swarm.py            (update to use new modules)
└── ...
```

### Running Multiple Experiments
```
Create in outputs/:
outputs/
├── animations/
│   ├── experiment_1_swarm_simulation.gif
│   ├── experiment_2_swarm_simulation.gif
│   ├── experiment_3_swarm_simulation.gif
│   └── ...
│
├── data/
│   ├── experiment_1_metrics.csv
│   ├── experiment_2_metrics.csv
│   ├── experiment_3_metrics.csv
│   └── ...
└── ...
```

### Versioning Configurations
```
config/
├── settings.py              (current/default)
├── settings_baseline.py     (original settings)
├── settings_large_swarm.py  (NUM_ROBOTS=30)
├── settings_many_obstacles.py (NUM_OBSTACLES=20)
└── ...
```

---

## ✅ Organization Benefits

### 1. **Clean Structure**
- Source code separate from outputs
- All results centralized
- Easy to find any file

### 2. **Scalability**
- Can run hundreds of simulations
- Each outputs to `outputs/` automatically organized
- No clutter in root directory

### 3. **Collaboration**
- Clear where to put new files
- Easy to share outputs
- Documentation in one place

### 4. **Version Control**
- `outputs/` typically excluded from Git
- Core code and configs in Git
- Reproducible from configs

### 5. **Reproducibility**
- Save config that ran each experiment
- All parameters documented in `config/settings.py`
- Results tied to specific configuration

---

## 🚀 Quick Navigation

**Want to...**
- **Run a simulation**: See `docs/QUICK_START.md`
- **Configure parameters**: Edit `config/settings.py`
- **View results**: Check `outputs/` folder
- **Understand structure**: You're reading it!
- **Create new feature**: Check `docs/PROJECT_SETUP.md`
- **Save results as video**: Run `scripts/save_animation.py`
- **Quick algorithm test**: Run `scripts/test_simulation.py`

---

## 📝 Summary

```
Quick Rules:
✓ All SCRIPTS       → scripts/
✓ All WINDOWS BATCH → batch_files/
✓ All OUTPUTS       → outputs/ (sub-folders by type)
✓ All DOCS          → docs/
✓ All CONFIG        → config/settings.py
✓ All SOURCE CODE   → src/
✓ Git Control       → .gitignore, .git/
```

**This organization keeps your project:**
- ✅ Organized and scalable
- ✅ Easy to navigate
- ✅ Ready for multiple simulations
- ✅ Professional and maintainable
- ✅ Ready for collaboration

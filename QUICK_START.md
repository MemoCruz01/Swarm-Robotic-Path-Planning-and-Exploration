# Quick Start Guide

## 🚀 Getting Started in 2 Minutes

### Step 1: Run the Test Simulation
```bash
python test_simulation.py
```
This runs a quick 200-iteration test without GUI. You'll see the swarm finding the target!

**Expected Output:**
```
✓ SUCCESS! Target found at iteration 9/10
Total iterations: 10
Robots near target: 4/15
Final exploration coverage: 5.0%
```

---

### Step 2: Run Full Simulation with Visualization
```bash
python main.py
```

**What You'll See:**
- **Left Side**: 2D visualization of robots exploring the environment
  - Blue circles = robots
  - Gray circles = obstacles
  - Red circle = target
  - Blue star = swarm center

- **Right Side**: Live statistics
  - Iteration counter
  - Fitness value
  - Exploration percentage
  - Distance to target
  - Robot speeds and spread

- **After Simulation**: Convergence plots showing
  - How fitness improves over time
  - Exploration coverage progression
  - Robot approach to target
  - Swarm velocity dynamics

---

## 📊 Understanding the Results

### What is Happening?
1. **15 robots** start at random positions
2. **PSO algorithm** guides each robot toward the **target at (80, 80)**
3. **Obstacles** force robots to navigate around them
4. **Collective behavior** emerges from simple rules

### Key Metrics
- **Best Fitness**: Higher is better (represents progress toward target)
- **Exploration Coverage**: % of environment visited
- **Robots Near Target**: Count of robots within 10 units of target
- **Swarm Spread**: How clustered/dispersed the swarm is

---

## 🎨 Customization Examples

### Make It Harder: More Obstacles
Edit `config/settings.py`:
```python
NUM_OBSTACLES = 15      # Instead of 8
OBSTACLE_MAX_SIZE = 10  # Instead of 8
```

### Make It Easier: More Robots
```python
NUM_ROBOTS = 30  # Instead of 15
```

### Change Target Location
```python
TARGET_X = 20
TARGET_Y = 20
```

### Run Longer Simulation
```python
PSO_ITERATIONS = 1000  # Instead of 500
```

---

## 📁 Project Files

| File | Purpose |
|------|---------|
| `main.py` | Full simulation with GUI visualization |
| `test_simulation.py` | Quick test without GUI (for debugging) |
| `config/settings.py` | All configurable parameters |
| `src/environment.py` | Environment, obstacles, target |
| `src/robot.py` | Individual robot behavior |
| `src/swarm.py` | Swarm coordination and statistics |
| `src/pso.py` | PSO algorithm core |
| `src/visualization.py` | Plotting and animation |
| `README.md` | Detailed documentation |
| `requirements.txt` | Python dependencies |

---

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'numpy'"
Solution:
```bash
pip install -r requirements.txt
```

### "No display found" (Linux/SSH)
The `test_simulation.py` script doesn't need display and works everywhere.

### Simulation runs very fast
Increase `VISUALIZATION_INTERVAL` in `config/settings.py` to see more frequent updates.

---

## 🎯 What's Happening Under the Hood?

### PSO Velocity Update
```
v_new = w*v + c1*r1*(best_pos - current_pos) + c2*r2*(global_best - current_pos)
```

Where:
- **w** = 0.7298 (inertia - momentum)
- **c1** = 1.49618 (cognitive - personal exploration)
- **c2** = 1.49618 (social - follow the swarm)

### Fitness Function
```
fitness = -distance_to_target + exploration_bonus - obstacle_penalty
```

The algorithm optimizes this fitness across all robots.

---

## 📈 Expected Performance

Typical results on default settings:
- **Target Found**: Within 10-50 iterations
- **Robots Near Target**: 3-8 robots
- **Exploration Coverage**: 5-15%
- **Time**: <5 seconds for 500 iterations

---

## 🔬 Advanced Features

### Save Animation
In `main.py`, change:
```python
run_simulation(save_animation=True)  # Saves as swarm_simulation.gif
```

### Custom Fitness Function
Edit `src/pso.py` method `fitness_function()` to prioritize:
- **Pure exploration** (ignore target)
- **Target first** (ignore exploration)
- **Formation control** (keep robots together)

### Disable Obstacle Avoidance
In `src/swarm.py`, comment out obstacle avoidance in `step()` method

---

## 💡 Ideas for Extension

1. **Multiple Targets**: Modify swarm to search for several locations
2. **Dynamic Obstacles**: Add moving obstacles
3. **Energy Constraints**: Add fuel/battery limitations
4. **Formation Control**: Make robots maintain specific patterns
5. **Communication Network**: Simulate limited information sharing
6. **Learning**: Use reinforcement learning instead of PSO
7. **3D Simulation**: Extend to 3D environments
8. **Real Robot Control**: Adapt code to control actual robots

---

## 📚 References

- Kennedy & Eberhart (1995): "Particle Swarm Optimization"
- Dorigo & Stützle (2019): "Ant Colony Optimization"
- Brambilla et al. (2013): "Swarm Robotics: A Review"

---

## ✓ You're Ready!

**Next: Run** `python test_simulation.py` **to see it in action!**

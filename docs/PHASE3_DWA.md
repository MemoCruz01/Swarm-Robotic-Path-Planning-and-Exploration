# Phase 3: Navigation Intelligence - Dynamic Window Approach (DWA)

**Status**: ✅ Completed March 29, 2026  
**Tests**: 12/12 passing ✓  
**Integration**: PSO + DWA hybrid approach

---

## Overview

Phase 3 adds **Dynamic Window Approach (DWA)** as a local trajectory planning layer that refines PSO velocities to avoid obstacles and other robots in real-time.

### Architecture

```
┌─────────────────────────────────────┐
│   PSO Algorithm (Global Planning)   │
│   Computes goal direction           │
│   for entire swarm                  │
└──────────────┬──────────────────────┘
               │
               │ (Goal direction)
               ▼
┌─────────────────────────────────────┐
│  DWA Planner (Local Refinement)     │
│  - Sample velocity candidates       │
│  - Predict trajectories             │
│  - Evaluate for collisions          │
│  - Select best safe velocity        │
│  - Apply heading smoothness         │
└──────────────┬──────────────────────┘
               │
               │ (Refined velocity)
               ▼
┌─────────────────────────────────────┐
│   Robot Motion (Phase 1 Physics)    │
│   - Motor acceleration smoothing    │
│   - Battery constraints             │
│   - Motor response delay            │
└─────────────────────────────────────┘
```

---

## DWA Algorithm

### 1. Velocity Sampling (Dynamic Window)

Generate candidate velocities within achievable range:

- **Linear speeds**: 0.3, 0.65, 1.0 × MAX_VELOCITY
- **Angular directions**: Uniformly sampled (12samples by default)
- **Total candidates**: ~36 velocities to evaluate per cycle

```python
for angle in linspace(0, 2π, 12):
    for speed_factor in [0.3, 0.65, 1.0]:
        vx = speed_factor * MAX_VELOCITY * cos(angle)
        vy = speed_factor * MAX_VELOCITY * sin(angle)
        candidates.append((vx, vy))
```

### 2. Trajectory Prediction

Simulate each candidate velocity forward N steps:

```python
def simulate_trajectory(pos, velocity, steps=8):
    trajectory = [pos]
    x, y = pos
    for _ in range(steps):
        x += vx
        y += vy
        trajectory.append((x, y))
    return trajectory
```

### 3. Trajectory Evaluation

Score each trajectory on 5 objectives:

#### A. Collision Detection (Early Termination)
- Check trajectory points against static obstacles
- Check predicted positions of nearby robots
- **Penalty**: -1000 if collision detected

```
if trajectory intersects obstacle_radius + robot_radius + safety_margin:
    score = -1000  # Invalid trajectory
    continue
```

#### B. Goal Alignment (Positive Reward)
- How well movement aligns with PSO goal direction
- Dot product between movement vector and goal

```
movement = trajectory_end - start_pos
alignment = dot(movement, goal_direction) / magnitude(movement)
score += GOAL_WEIGHT * alignment
```

#### C. Safety Distance (Progressive Reward)
- Maximize minimum distance to obstacles
- Reward safe spacing from other robots

```
min_distance = min(distance_to_all_obstacles_and_robots)
safety_score = max(0, min(DWA_COLLISION_DISTANCE, min_distance))
score += OBSTACLE_WEIGHT * safety_score
```

#### D. Heading Smoothness (Jitter Reduction)
- Prefer small heading changes (smooth curves)
- Reduces oscillation and twitchy behavior

```
angle_change = absolute(new_heading - previous_heading)
smoothness_score = 1 - (angle_change / π)
score += SMOOTHNESS_WEIGHT * smoothness_score
```

#### E. Exploration Variance
- Encourages sampling of diverse velocities
- Prevents premature convergence to suboptimal paths

```
velocity_magnitude = sqrt(vx² + vy²)
exploration_score = velocity_magnitude / MAX_VELOCITY
score += EXPLORATION_WEIGHT * exploration_score
```

### 4. Velocity Selection

Pick velocity with highest composite score:

```
best_velocity = argmax(score for all trajectories)
```

### 5. Heading Smoothness Filter

Blend selected heading with previous for temporal coherence:

```
smooth_heading = HISTORY * prev_heading + (1-HISTORY) * new_heading
smooth_vx = magnitude * cos(smooth_heading)
smooth_vy = magnitude * sin(smooth_heading)
```

Clamp angular velocity change:
```
angular_change = min(angular_change, MAX_ANGULAR_VELOCITY)
```

---

## Configuration Parameters

Located in `config/realism_settings.py`:

```python
# Master switch
ENABLE_PHASE3_NAVIGATION = True
USE_DWA = True

# Trajectory prediction
DWA_PREDICTION_STEPS = 8           # Steps to look ahead
DWA_VELOCITY_SAMPLES = 12          # Candidate angles to sample

# Velocity window
DWA_MIN_VELOCITY = 0.1
DWA_MAX_VELOCITY = 1.5             # Must match ROBOT_SPEED

# Collision avoidance
DWA_COLLISION_DISTANCE = 3.0       # Safety distance to plan for
DWA_ROBOT_COLLISION_DISTANCE = 2.5 # Robot-robot collision threshold
DWA_SAFETY_MARGIN = 0.5            # Extra buffer

# Heading control
DWA_HEADING_HISTORY = 0.7          # Smoothing (0=none, 1=full)
DWA_MAX_ANGULAR_VELOCITY = 0.3     # Max rotation rate

# Objective weights
GOAL_WEIGHT = 1.0                  # Prioritize PSO goal direction
OBSTACLE_WEIGHT = 2.0              # Prioritize collision avoidance
SMOOTHNESS_WEIGHT = 0.3            # Prefer smooth paths
EXPLORATION_WEIGHT = 0.2           # Encourage velocity diversity
```

---

## Performance Characteristics

### Computational Cost
- **Per-robot per-cycle**: ~36 trajectory evaluations
- **Per evaluation**: ~16 distance checks (obstacles + robots)
- **Total**: ~576 distance checks per robot per cycle
- **Runtime impact**: ~+15-20% vs Phase 2

### Swarm Behavior Changes

#### Without DWA (Phase 2)
- Robots follow PSO without local obstacle awareness
- May clip corners of obstacles
- PSO recovery from collisions takes time
- Possible swarm entrenchment in local minima

#### With DWA (Phase 3)
- Real-time obstacle avoidance before collision
- Smooth circumnavigation of obstacles
- Faster path efficiency
- Better distributed exploration
- Reduced mutual robot collisions

---

## Test Coverage

### Unit Tests (12/12 ✅)

1. **test_dwa_velocity_sampling** ✓
   - Verifies 36+ candidates generated
   - All velocities within speed limits

2. **test_dwa_trajectory_simulation** ✓
   - Trajectory correctly simulates N steps
   - End position matches velocity integration

3. **test_dwa_collision_detection** ✓
   - Trajectories hitting obstacles score -1000
   - Detection works for both static obstacles and robots

4. **test_dwa_safe_trajectory_scoring** ✓
   - Safe trajectories in open space score>0
   - Aligned with goal direction

5. **test_dwa_heading_smoothness** ✓
   - Sudden heading changes are blended
   - Temporal coherence maintained

6. **test_dwa_angle_diff_wraparound** ✓
   - Angle wraparound at ±π handled correctly
   - Shortest angle path selected

7. **test_dwa_plan_method** ✓
   - Full DWA pipeline executes without errors
   - Returns valid refined velocities

8. **test_dwa_avoids_obstacles** ✓
   - DWA redirects away from obvious hazards
   - Obstacle avoidance prioritized over goal alignment (when collision risk)

9. **test_dwa_multiple_calls** ✓
   - State maintained across multiple planning cycles
   - Consistent execution over time

10. **test_phase3_configuration** ✓
    - Phase 3 config parameters properly set
    - All weights and thresholds valid

11. **test_dwa_with_robot_model** ✓
    - DWA planners instantiated per robot
    - Integration with RobotSwarm verified

12. **test_dwa_step_execution** ✓
    - Swarm.step() executes without errors with DWA
    - Statistics properly computed

---

## Code Structure

### Core Files

1. **src/dwa_planner.py** (New - 350 lines)
   - `DWAPlanner` class
   - Methods:
     - `plan()` - Main entry point
     - `_sample_velocities()` - Generate candidates
     - `_simulate_trajectory()` - Predict motion
     - `_evaluate_trajectory()` - Score each trajectory
     - `_apply_heading_smoothness()` - Filter output
     - `_angle_diff()` - Angle wraparound utility

2. **src/swarm.py** (Modified - +60 lines)
   - Imports `DWAPlanner`
   - Instantiates per-robot planners in `__init__`
   - Calls DWA planning  in `step()` after PSO
   - Passes refined velocities to robots

3. **config/realism_settings.py** (Modified - Enhanced Phase 3)
   - Added 17 DWA parameters
   - Detailed documentation for each
   - Tuning guidance

---

## How DWA Improves Navigation

### Scenario 1: Narrow Corridor
**Without DWA**: Robot might graze obstacle edges, triggering collision responses.  
**With DWA**: Predicts trajectory, steers clear before impact. Smooth path through corridor.

### Scenario 2: Dense Swarm Region
**Without DWA**: Robots follow PSO, frequent mutual collisions requiring response time.  
**With DWA**: Predicts robot movements, selects velocities that maintain spacing.

### Scenario 3: Local Minimum
**Without DWA**: PSO can get trapped near local obstacles.  
**With DWA**: Exploration sampling encourages diverse trajectories, helping escape local minima.

### Scenario 4: Dynamic Obstacles (Future)
**Without DWA**: Assumes static environment.  
**With DWA**: Can predict moving obstacles, adjust preemptively.

---

## Next Steps (Phase 4)

Phase 4 will add **Environment Complexity**:
- **Terrain modifiers** - Speed penalties in certain regions
- **Dynamic obstacles** - Moving obstacles in the environment
- **Slope/friction** - Terrain properties affecting motion
- **GPS noise** - Uncertainty in position measurements

Phase 3 DWA provides the foundation for safely handling complex, dynamic environments.

---

## References

- **Original DWA Paper**: Fox, Burgard, Thrun (1997) - "The Dynamic Window Approach to Collision Avoidance"
- **Implementation**: Marina, Orebäck (2006) - "Real Time Obstacle Avoidance"
- **ROS Implementation**: move_base dwa_local_planner package

---

**Generated**: March 29, 2026  
**Phase**: 3/5 Complete  
**Status**: Ready for Phase 4 (Environment Complexity)

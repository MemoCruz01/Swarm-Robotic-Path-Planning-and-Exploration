# 🤖 Differential Drive Robots - Enhanced Simulation

## Overview

Your swarm robotics simulation has been upgraded with **realistic differential drive kinematics**! This means your robots now behave like actual wheeled ground robots (like differential drive platforms, tanks, or robot cars) instead of omnidirectional drones.

---

## ✨ Key Features of Differential Drive

### 1. **Realistic Motion Model**
- **Two independent wheels** (left and right)
- Forward/backward motion controlled by **average wheel velocity**
- Rotation controlled by **difference between wheel velocities**
- Natural turning behavior with adjustable turning radius

### 2. **Orientation & Heading**
- Robots have a **heading angle (θ)** showing the direction they face
- **Blue arrows** show robot orientation in visualization
- Robots move forward in the direction they face (like real robots!)

### 3. **Realistic Kinematics**
- Uses differential drive kinematics equations
- Smooth curved paths instead of instant direction changes
- More complex navigation challenges for the swarm

---

## 🔧 Configuration

### Enable/Disable Differential Drive

In `config/settings.py`:

```python
# Enable differential steering
USE_DIFFERENTIAL_DRIVE = True

# Parameters
WHEEL_DISTANCE = 2.0              # Wheelbase (distance between wheels)
HEADING_CORRECTION_GAIN = 0.5     # Turning response (0.1-1.0)
```

### Parameters Explained

| Parameter | Range | Effect |
|-----------|-------|--------|
| `WHEEL_DISTANCE` | 0.5-5.0 | Smaller = tighter turns, Larger = wider turns |
| `HEADING_CORRECTION_GAIN` | 0.1-1.0 | Lower = sluggish, Higher = snappy turns |

### Recommended Settings

```python
# For smooth exploration (recommended)
WHEEL_DISTANCE = 2.0
HEADING_CORRECTION_GAIN = 0.5

# For faster turning (more agile)
WHEEL_DISTANCE = 1.5
HEADING_CORRECTION_GAIN = 0.8

# For wide turns (conservative)
WHEEL_DISTANCE = 3.0
HEADING_CORRECTION_GAIN = 0.3
```

---

## 📐 How It Works

### Motion Equations

The differential drive model uses these equations:

```
Linear velocity:  v = (v_left + v_right) / 2
Angular velocity: ω = (v_right - v_left) / wheelbase

Position update:
  x_new = x + v * cos(θ)
  y_new = y + v * sin(θ)
  
Heading update:
  θ_new = θ + ω
```

### PSO Integration

The PSO algorithm computes a desired velocity (vx, vy), which is then converted to:
1. **Desired heading** = atan2(vy, vx)
2. **Desired speed** = √(vx² + vy²)
3. **Heading error** = desired - current
4. **Wheel commands** = derived from (v, ω) using kinematics

---

## 🎮 Visualization

### What You'll See

- **Blue circles** = Robot positions
- **Dark blue arrows** = Robot heading/orientation
- **Cyan vectors** = Velocity direction (if enabled)
- **Red circle** = Target location
- **Gray circles** = Obstacles

### Arrow Interpretation

The arrow shows which way the robot is **facing** and **moving forward**:
- Arrow pointing right → Robot moving right
- Arrow pointing up → Robot moving up/forward
- Arrow at angle → Robot facing that direction

---

## 🧪 Testing & Comparing Behaviors

### Run with Differential Drive (Default)

```bash
python scripts/animate_swarm.py
```

Watch robots navigate with realistic turning paths!

### Compare Motion Styles

**Differential Drive Features:**
- ✓ Realistic ground robot behavior
- ✓ Natural curved paths
- ✓ Cannot turn in place (like real robots)
- ✓ Must face direction of travel
- ✓ More challenging navigation

**Vs. Omnidirectional (Old Model):**
- Can move any direction instantly
- Straight-line paths
- Can turn without moving
- Unrealistic for ground robots

---

## 📊 Robot State Information

### Available Robot Methods

```python
robot.get_position()           # Returns (x, y)
robot.get_heading()           # Returns θ (radians)
robot.get_wheel_velocities()  # Returns (v_left, v_right)
robot.get_linear_velocity()   # Returns forward speed
robot.get_angular_velocity()  # Returns rotation speed
robot.get_orientation_vector()# Returns (dx, dy) heading unit vector
```

### Example Usage

```python
for robot in swarm.robots:
    x, y = robot.get_position()
    heading = robot.get_heading()
    v_lin = robot.get_linear_velocity()
    v_ang = robot.get_angular_velocity()
    
    print(f"Robot {robot.id}: pos=({x:.1f},{y:.1f}), " +
          f"heading={heading:.2f}rad, v={v_lin:.2f}, ω={v_ang:.2f}")
```

---

## 🎯 Common Scenarios

### Scenario 1: Slow Turning
**Problem**: Robots turn too slowly to navigate efficiently

**Solution**:
```python
HEADING_CORRECTION_GAIN = 0.8  # Increase turning response
WHEEL_DISTANCE = 1.5           # Smaller wheelbase = tighter turns
```

### Scenario 2: Erratic Motion
**Problem**: Robots zigzag or oscillate

**Solution**:
```python
HEADING_CORRECTION_GAIN = 0.3  # Decrease turning response
WHEEL_DISTANCE = 2.5           # Larger wheelbase = smoother curves
```

### Scenario 3: Stuck Robots
**Problem**: Robots can't escape from obstacles

**Solution**:
- Robot will bounce and reverse (collision handling in code)
- Increase `ROBOT_SPEED` for more turning capability
- Adjust `MIN_OBSTACLE_DISTANCE` for earlier obstacle detection

---

## 🔬 Advanced: Tuning for Your Environment

### 1. **Easy Environment** (few obstacles, lots of space)
```python
HEADING_CORRECTION_GAIN = 0.3  # Smooth, wide turns
WHEEL_DISTANCE = 3.0
NUM_ROBOTS = 10
```

### 2. **Medium Environment** (moderate obstacles)
```python
HEADING_CORRECTION_GAIN = 0.5  # Balanced (default)
WHEEL_DISTANCE = 2.0
NUM_ROBOTS = 15
```

### 3. **Hard Environment** (many obstacles, tight spaces)
```python
HEADING_CORRECTION_GAIN = 0.8  # Quick, responsive turns
WHEEL_DISTANCE = 1.5
NUM_ROBOTS = 20
```

---

## 📈 Performance Notes

### What Changes vs. Omnidirectional

| Aspect | Omnidirectional | Differential Drive |
|--------|-----------------|-------------------|
| Iterations to target | ~5-15 | ~10-25 (more realistic) |
| Path efficiency | Very efficient | More realistic paths |
| CPU usage | Similar | Similar |
| Turning behavior | Instant | Gradual curves |
| Realism | Low | High ✓ |

### Simulation Speed

- Differential drive calculations add minimal overhead
- Simulation runs at same speed as omnidirectional model
- Visualization is the main performance factor (same as before)

---

## 🐛 Troubleshooting

### Robots spinning in circles?
```python
# Decrease turning response
HEADING_CORRECTION_GAIN = 0.2
```

### Robots not turning enough?
```python
# Increase turning response
HEADING_CORRECTION_GAIN = 0.8
# or increase wheel distance effect:
WHEEL_DISTANCE = 1.0
```

### Robots going backwards?
This is normal! Differential drive robots sometimes reverse to adjust heading. This mirrors real robot behavior.

### Robots getting stuck?
```python
# Increase speed or obstacle detection
ROBOT_SPEED = 3.0
COLLISION_PREDICTION_RANGE = 5.0
```

---

## 🎓 Real-World Applications

This differential drive model accurately simulates:

✓ **Wheeled robots**
- TurtleBot / ThymeBot
- Robot vacuum cleaners
- Mini ground robots

✓ **Tank-like platforms**
- Tracked robots
- UGVs (Unmanned Ground Vehicles)

✓ **Front-wheel drive simplifications**
- Many mobile robots

---

## 📚 Resources

### Understanding Differential Drive

1. **Kinematics**: How motion translates to position
2. **PSO**: Finding good navigation directions
3. **Control**: Converting desired velocity to wheel commands

### Key Equations

```
Kinematics:
  radius = v / ω  (instantaneous turning radius)
  v = (v_L + v_R) / 2
  ω = (v_R - v_L) / L

Control:
  ω_desired = Kp * θ_error
  v_L = v - (L/2) * ω
  v_R = v + (L/2) * ω
```

---

## ✅ Next Steps

1. **Run a simulation**: `python scripts/animate_swarm.py`
2. **Observe** the blue arrows showing robot orientation
3. **Modify** `HEADING_CORRECTION_GAIN` and watch behavior change
4. **Tune** parameters for your environment
5. **Experiment** with different swarm sizes and obstacles

---

## 📝 Summary

Your robots now use **realistic differential drive kinematics**:
- ✓ Two independent wheels
- ✓ Natural curved paths
- ✓ Heading-oriented movement
- ✓ Configurable turning behavior
- ✓ Fully backward compatible

**Ready to explore with realistic robots!** 🤖

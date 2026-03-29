# Guide: Configuring Simulation Stopping Conditions

This file explains how to control when the simulation stops based on target achievement.

---

## 🎯 QUICK REFERENCE

### OPTION 1: Stop when first robot reaches target ⚡
```python
STOP_ON_SINGLE_ROBOT = True       # ✓ Enable
STOP_ON_ALL_ROBOTS = False        # ✗ Disable
STOP_ON_PERCENTAGE = False        # ✗ Disable
```
**Result**: Stops immediately when ANY robot enters red target area

---

### OPTION 2: Stop when all robots reach target 🤝
```python
STOP_ON_SINGLE_ROBOT = False      # ✗ Disable
STOP_ON_ALL_ROBOTS = True         # ✓ Enable
STOP_ON_PERCENTAGE = False        # ✗ Disable
```
**Result**: Continues until ALL 15 robots are in target zone (best for coordinated missions)

---

### OPTION 3: Stop when 80% of robots reach target ⭐ RECOMMENDED
```python
STOP_ON_SINGLE_ROBOT = False      # ✗ Disable
STOP_ON_ALL_ROBOTS = False        # ✗ Disable
STOP_ON_PERCENTAGE = True         # ✓ Enable
TARGET_ROBOT_PERCENTAGE = 80      # 80% = ~12 out of 15 robots
```
**Result**: Stops when majority (80%) reach target (good balance)

---

### OPTION 4: Run until all iterations complete 📊
```python
STOP_ON_SINGLE_ROBOT = False      # ✗ Disable
STOP_ON_ALL_ROBOTS = False        # ✗ Disable
STOP_ON_PERCENTAGE = False        # ✗ Disable
```
**Result**: Runs full duration regardless of target (useful for studying algorithm)

---

## 📍 What is the Target Zone?

The target is a **RED CIRCLE** at:
- **Location**: (80, 80)
- **Radius**: 5 units

A robot is considered "IN TARGET" if it's within the radius of (80, 80)

Default settings in `config/settings.py`:
```python
TARGET_X = 80
TARGET_Y = 80
TARGET_RADIUS = 5
```

---

## 🛠️ How to Change Settings

1. **Open**: `config/settings.py`
2. **Find section**: "Simulation Stopping Conditions"
3. **Change the TRUE/FALSE values**
4. **Save the file**
5. **Run simulation**: 
   ```bash
   python scripts/animate_swarm.py
   # OR
   python scripts/save_animation.py
   ```

---

## 💡 Testing Examples

### Example 1: Stop when majority reaches target (80%)
Edit in `config/settings.py`:
```python
STOP_ON_SINGLE_ROBOT = False
STOP_ON_ALL_ROBOTS = False
STOP_ON_PERCENTAGE = True
TARGET_ROBOT_PERCENTAGE = 80  # 80% of robots required
```

Run: `python scripts/animate_swarm.py`

**Expected**: Animation stops after ~10-15 iterations when enough robots converge

---

### Example 2: Let everyone reach target
Edit in `config/settings.py`:
```python
STOP_ON_SINGLE_ROBOT = False
STOP_ON_ALL_ROBOTS = True    # ← Changed this
STOP_ON_PERCENTAGE = False
```

Run: `python scripts/animate_swarm.py`

**Expected**: Animation continues until all 15 robots enter target zone

---

### Example 3: Stop immediately when first robot reaches
Edit in `config/settings.py`:
```python
STOP_ON_SINGLE_ROBOT = True  # ← Changed this
STOP_ON_ALL_ROBOTS = False
STOP_ON_PERCENTAGE = False
```

Run: `python scripts/animate_swarm.py`

**Expected**: Animation stops very quickly (first robot reaches target fast)

---

## 🌍 Real-World Analogies

### STOP_ON_SINGLE_ROBOT
**Like**: Search and rescue finding first survivor
**Use**: When you just need to find something quickly
**Example**: Searching for a lost hiker - stop when first person found

---

### STOP_ON_ALL_ROBOTS
**Like**: Military unit ensuring all soldiers reach rally point
**Use**: When perfect coordination is critical
**Example**: Formation flying of drone swarm - all must arrive together

---

### STOP_ON_PERCENTAGE (80%)
**Like**: School field trip - depart when most students arrive
**Use**: Balance between efficiency and ensuring coverage
**Example**: Mapping team coverage - most areas explored, few stragglers

---

## 👀 Visual Feedback

When simulation stops, you'll see in the terminal:

```
✓ CONDITION MET: 80% of robots (12/15) reached target!
```

And in the animation window:
- Most robots will be IN the red target area
- Info panel shows "robots_near_target" count
- Simulation stops (window stays open until you close it)

---

## 📈 CURRENT DEFAULT

From `config/settings.py`:
```python
STOP_ON_SINGLE_ROBOT = False
STOP_ON_ALL_ROBOTS = False
STOP_ON_PERCENTAGE = True
TARGET_ROBOT_PERCENTAGE = 100  # Latest: stops at 100% (all robots)
```

**This means**: Simulation stops when 100% of robots (ALL 15) reach the target

---

## ⚙️ Advanced: Custom Percentages

You can use any percentage:

```python
TARGET_ROBOT_PERCENTAGE = 50   # Stop at 50% (8/15 robots) - very loose
TARGET_ROBOT_PERCENTAGE = 75   # Stop at 75% (11/15 robots)
TARGET_ROBOT_PERCENTAGE = 90   # Stop at 90% (13/15 robots)
TARGET_ROBOT_PERCENTAGE = 100  # Stop at 100% (15/15 robots) - strict
```

**Calculation**: actual_count = NUM_ROBOTS * (TARGET_ROBOT_PERCENTAGE / 100)

So if `NUM_ROBOTS = 15` and `TARGET_ROBOT_PERCENTAGE = 80`:
- Required robots = 15 * 0.80 = **12 robots**
- Stops when 12 (or more) robots reach target

---

## 📊 Performance Comparison

| Setting | Iterations | Time | Purpose |
|---------|-----------|------|---------|
| STOP_ON_SINGLE_ROBOT | ~5-8 | <5 sec | Quick success check |
| STOP_ON_PERCENTAGE=50% | ~10-15 | ~10 sec | Loose coordination |
| STOP_ON_PERCENTAGE=80% | ~15-25 | ~15 sec | Balanced (RECOMMENDED) |
| STOP_ON_ALL_ROBOTS | ~30-50 | ~30 sec | Strict coordination |
| Run full duration | ~500 | ~60 sec | Complete analysis |

---

## 🔍 Which Option to Choose?

**Choose STOP_ON_SINGLE_ROBOT if**:
- You want quick success (doesn't need all robots)
- Testing algorithm efficiency
- Shortest simulation time

**Choose STOP_ON_ALL_ROBOTS if**:
- All robots MUST reach target (mission-critical)
- Strict formation flying needed
- Willing to wait longer

**Choose STOP_ON_PERCENTAGE (RECOMMENDED) if**:
- Most robots near target is good enough
- Balancing efficiency and coverage
- Realistic mission scenarios
- **Try 80% as default**

**Choose NONE (run full duration) if**:
- Studying algorithm convergence
- Analyzing swarm behavior over time
- Need complete performance data
- Research or academic purposes

---

## 🐛 Troubleshooting

**Simulation never stops**:
- Check that none of the STOP_ON_* options are enabled
- Verify TARGET_X and TARGET_Y are reachable (not blocked by obstacles)
- Increase NUM_ROBOTS for faster target reach

**Stops too quickly**:
- Decrease TARGET_ROBOT_PERCENTAGE (from 80% to 50%)
- Enable STOP_ON_PERCENTAGE instead of STOP_ON_SINGLE_ROBOT

**Stops too late**:
- Increase TARGET_ROBOT_PERCENTAGE (from 80% to 100%)
- Enable STOP_ON_SINGLE_ROBOT instead

---

## 📝 Common Configurations

### Fast Test (for debugging)
```python
STOP_ON_SINGLE_ROBOT = True
STOP_ON_ALL_ROBOTS = False
STOP_ON_PERCENTAGE = False
```

### Balanced Mission (RECOMMENDED)
```python
STOP_ON_SINGLE_ROBOT = False
STOP_ON_ALL_ROBOTS = False
STOP_ON_PERCENTAGE = True
TARGET_ROBOT_PERCENTAGE = 80
```

### Strict Coordination
```python
STOP_ON_SINGLE_ROBOT = False
STOP_ON_ALL_ROBOTS = True
STOP_ON_PERCENTAGE = False
```

### Full Analysis
```python
STOP_ON_SINGLE_ROBOT = False
STOP_ON_ALL_ROBOTS = False
STOP_ON_PERCENTAGE = False
```

---

## ✓ Summary

1. **Edit** `config/settings.py`
2. **Set exactly ONE** of the STOP_ON_* options to True
3. **If using STOP_ON_PERCENTAGE**, also set TARGET_ROBOT_PERCENTAGE
4. **Save and run** your simulation
5. **Watch** robots navigate and stop when condition is met!

**Try STOP_ON_PERCENTAGE = 80% for best results!**

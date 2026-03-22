"""
Guide: Configuring Simulation Stopping Conditions

This file explains how to control when the simulation stops based on target achievement.
"""

# ============================================================================
# STOPPING CONDITIONS CONFIGURATION
# ============================================================================

# Location: config/settings.py
# Variables:
#   STOP_ON_SINGLE_ROBOT      - Stop when ANY robot reaches target
#   STOP_ON_ALL_ROBOTS        - Stop when ALL robots reach target  
#   STOP_ON_PERCENTAGE        - Stop when X% of robots reach target
#   TARGET_ROBOT_PERCENTAGE   - What % is required (if using STOP_ON_PERCENTAGE)

# ============================================================================
# QUICK REFERENCE
# ============================================================================

# OPTION 1: Stop when first robot reaches target
STOP_ON_SINGLE_ROBOT = True       # ✓ Enable
STOP_ON_ALL_ROBOTS = False        # ✗ Disable
STOP_ON_PERCENTAGE = False        # ✗ Disable

# Result: Simulation stops immediately when any robot enters red target area


# ============================================================================

# OPTION 2: Stop when all robots reach target
STOP_ON_SINGLE_ROBOT = False      # ✗ Disable
STOP_ON_ALL_ROBOTS = True         # ✓ Enable
STOP_ON_PERCENTAGE = False        # ✗ Disable

# Result: Simulation continues until all 15 robots are in target zone
# (Best for coordinated team missions)


# ============================================================================

# OPTION 3: Stop when 80% of robots reach target (RECOMMENDED)
STOP_ON_SINGLE_ROBOT = False      # ✗ Disable
STOP_ON_ALL_ROBOTS = False        # ✗ Disable
STOP_ON_PERCENTAGE = True         # ✓ Enable
TARGET_ROBOT_PERCENTAGE = 80      # 80% = ~12 out of 15 robots

# Result: Simulation stops when majority (80%) reach target
# (Good balance between efficiency and coverage)


# ============================================================================

# OPTION 4: Run until all 500 iterations complete
STOP_ON_SINGLE_ROBOT = False      # ✗ Disable
STOP_ON_ALL_ROBOTS = False        # ✗ Disable
STOP_ON_PERCENTAGE = False        # ✗ Disable

# Result: Simulation runs full duration regardless of target
# (Useful for studying full algorithm behavior)


# ============================================================================
# WHAT IS THE TARGET ZONE?
# ============================================================================

# The target is a RED CIRCLE at:
#   Location: (80, 80)
#   Radius: 5 units
#
# A robot is considered "IN TARGET" if it's within the radius of (80, 80)

# Current settings in config/settings.py:
TARGET_X = 80
TARGET_Y = 80
TARGET_RADIUS = 5


# ============================================================================
# HOW TO CHANGE SETTINGS
# ============================================================================

# 1. Open: config/settings.py
# 2. Find the section: "Simulation Stopping Conditions"
# 3. Change the TRUE/FALSE values
# 4. Save the file
# 5. Run simulation: python animate_swarm.py  OR  python save_animation.py


# ============================================================================
# TESTING EXAMPLES
# ============================================================================

# Example 1: To stop when majority reaches target
Edit in config/settings.py:
    STOP_ON_SINGLE_ROBOT = False
    STOP_ON_ALL_ROBOTS = False
    STOP_ON_PERCENTAGE = True
    TARGET_ROBOT_PERCENTAGE = 80  # 80% of robots required
    
Run: python animate_swarm.py
Expected: Animation stops after ~10-15 iterations when enough robots converge


# Example 2: To let everyone reach target
Edit in config/settings.py:
    STOP_ON_SINGLE_ROBOT = False
    STOP_ON_ALL_ROBOTS = True    # ← Changed
    STOP_ON_PERCENTAGE = False
    
Run: python animate_swarm.py
Expected: Animation continues until all 15 robots enter target zone


# Example 3: To stop immediately when first robot reaches
Edit in config/settings.py:
    STOP_ON_SINGLE_ROBOT = True   # ← Changed
    STOP_ON_ALL_ROBOTS = False
    STOP_ON_PERCENTAGE = False
    
Run: python animate_swarm.py
Expected: Animation stops very quickly (first robot reaches target fast)


# ============================================================================
# REAL-WORLD ANALOGIES
# ============================================================================

# STOP_ON_SINGLE_ROBOT:
#   Like: Search and rescue finding first survivor
#   Use: When you just need to find something quickly
#
# STOP_ON_ALL_ROBOTS:
#   Like: Military unit ensuring all soldiers reach rally point
#   Use: When perfect coordination is critical
#
# STOP_ON_PERCENTAGE (80%):
#   Like: School field trip - depart when most students arrive
#   Use: Balance between efficiency and ensuring coverage
#   (Recommended for most scenarios)


# ============================================================================
# VISUAL FEEDBACK
# ============================================================================

# When simulation stops, you'll see in the terminal:
#
# ✓ CONDITION MET: 80% of robots (12/15) reached target!
#
# And in the animation window:
#   - Most robots will be RED target area
#   - Info panel shows "robots_near_target" count increasing
#   - Simulation stops, but window stays open until you close it


# ============================================================================
# CURRENT DEFAULT (from last run)
# ============================================================================

# config/settings.py currently has:
STOP_ON_SINGLE_ROBOT = False
STOP_ON_ALL_ROBOTS = False
STOP_ON_PERCENTAGE = True
TARGET_ROBOT_PERCENTAGE = 80

# This means: Simulation stops when 80% of robots (12 out of 15) reach the target

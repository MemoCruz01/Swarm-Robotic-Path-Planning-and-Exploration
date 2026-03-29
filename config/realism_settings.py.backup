"""
Realism settings for advanced physics features (Phase 1+).
Organized by feature with detailed comments.
All features can be individually enabled/disabled.

Created: March 29, 2026
Version: 3.0 (Phase 1 - Core Physics)
"""

# ============================================================================
# PHASE 1: CORE PHYSICS (March 29, 2026)
# ============================================================================

# --- Master Switch ---
ENABLE_PHASE1_PHYSICS = True  # Set to False to disable all Phase 1 features

# --- Battery/Energy Management ---
BATTERY_ENABLED = True
"""
When enabled, robots have finite battery that drains with movement.
Robots must return to home base (0, 0) to recharge.

Physics model:
  - Idle drain: small constant power draw
  - Speed drain: proportional to (v_left² + v_right²)
  - Realistic: higher speeds cost exponentially more energy
  - Emergent behavior: PSO learns energy-efficient paths
"""
BATTERY_INITIAL = 100.0                # Start with full battery (%)
BATTERY_DRAIN_RATE = 0.05              # % per update, idle/constant loss
BATTERY_SPEED_PENALTY = 0.015          # % per (m/s)²; total_drain = rate + speed_penalty * v²
BATTERY_LOW_THRESHOLD = 20             # Below this %, reduce speed
BATTERY_LOW_SPEED_MULTIPLIER = 0.5     # Scale velocity to 50% when low on battery
BATTERY_RECHARGE_DISTANCE = 3.0        # Radius around (0,0) to trigger recharge
BATTERY_RECHARGE_RATE = 2.0            # Recharge 2x faster than drain (% per step)
BATTERY_MIN_RECHARGE_THRESHOLD = 80    # Stop charging at 80% (leave room for full)

# --- Motor Acceleration Limits ---
SMOOTH_ACCELERATION = True
"""
When enabled, robot wheels ramp up/down smoothly.
Instead of instant velocity changes, accelerate gradually.

Physics model:
  - PSO computes desired wheel velocities
  - Actual velocity smoothly approaches desired by MAX_ACCELERATION per frame
  - Realistic: electric motors can't change speed instantly
  - Visual benefit: smooth curves instead of jerky angular motion
"""
MAX_ACCELERATION = 0.5                 # Units per simulation step
                                       # Higher = faster acceleration / more twitchy
                                       # Lower = sluggish / more realistic motors

# --- Motor Response Delay ---
MOTOR_RESPONSE_DELAY = 2               # Frames of latency (0 = no delay, disabled)
"""
When > 0, commands are queued and applied N frames later.

Physics model:
  - PSO sends command at frame T
  - Command is queued
  - Command is applied at frame T+N
  - Navigation become harder due to latency
  - Realistic: USB latency, WiFi lag, onboard processing time

Typical values:
  - 0 = no delay (disabled)
  - 1 = minimal (one frame latency)
  - 2 = moderate (slightly sluggish) - RECOMMENDED
  - 3+ = high (hard to control)
"""

# --- Visualization & Display ---
SHOW_BATTERY_STATUS = True             # Display battery bar in animation
SHOW_VELOCITY_PROFILE = False          # Optional: show acceleration smoothing graph

# --- Debugging ---
DEBUG_PHASE1 = False                   # Print debug info to console
LOG_ENERGY_STATS = False               # Log battery/energy stats each step


# ============================================================================
# PHASE 2: ROBOT INTERACTION (March 29, 2026)
# ============================================================================

# --- Master Switch ---
ENABLE_PHASE2_INTERACTION = True  # Set to False to disable all Phase 2 features

# --- Robot-Robot Collisions ---
ROBOT_COLLISIONS_ENABLED = True
"""
When enabled, robots detect and handle collisions with each other.

Physics model:
  - Each frame, check all robot pairs for collision
  - Collision if center-to-center distance < 2*ROBOT_RADIUS
  - Response: push robots apart + bouncy reflection
  - Elasticity: 0=stick together, 0.7=bounce, 1.0=perfect bounce
  - Realistic: prevents robot stacking, models physical contacts
"""
ROBOT_RADIUS = 1.0                     # Size of robot for collision detection (units)
COLLISION_ELASTICITY = 0.7             # Bounce factor: 0=inelastic, 1.0=bouncy
COLLISION_SEPARATION_SPEED = 0.3       # How fast to push apart on collision

# --- Multi-Agent Communication ---
COMMUNICATION_RANGE_ENABLED = True
"""
When enabled, robots only share PSO best positions with nearby teammates.

Physics model:
  - Each robot has communication range (e.g., 20 units)
  - Only robots within range can exchange PSO best positions
  - Creates local coordination clusters
  - Realistic: WiFi range, communication line-of-sight
  - Emergent behavior: swarm self-organizes into sub-swarms
"""
COMMUNICATION_RANGE = 20.0             # Maximum distance for neighbor communication (units)
SKIP_COMMUNICATION_WITH_SELF = True    # Don't double-count robot's own best position
COMMUNICATION_RANGE_METHOD = "euclidean"  # "euclidean" or "line_of_sight" (future)

# --- Flocking Behavior (DISABLED FOR PHASE 2) ---
FLOCKING_BEHAVIOR = False              # Optional: Boid-style swarm behavior (Phase 2+)
SEPARATION_RANGE = 5.0                 # Distance triggering separation force (future)
SEPARATION_WEIGHT = 1.0                # How strong to avoid crowding (future)
ALIGNMENT_WEIGHT = 0.5                 # Match neighbor headings (future)
COHESION_WEIGHT = 0.3                  # Move toward center of neighbors (future)

# --- Debugging ---
DEBUG_PHASE2 = False                   # Print collision/communication debug info
LOG_COLLISION_STATS = False            # Log collision events each step


# ============================================================================
# PHASE 3: NAVIGATION INTELLIGENCE (March 29, 2026)
# ============================================================================
# Dynamic Window Approach (DWA) for local trajectory planning

# --- Master Switch ---
ENABLE_PHASE3_NAVIGATION = True  # Set to False to disable DWA refinement

# --- DWA Core Parameters ---
USE_DWA = True                         # Enable Dynamic Window Approach
DWA_PREDICTION_STEPS = 8               # Look ahead N steps for trajectory prediction
DWA_VELOCITY_SAMPLES = 12              # Number of velocity candidates to evaluate
DWA_ANGULAR_STEP = 0.3                # Angular velocity step size for sampling
DWA_LINEAR_STEP = 0.2                 # Linear velocity step size for sampling
DWA_MIN_VELOCITY = 0.1                # Minimum forward velocity (units/step)
DWA_MAX_VELOCITY = 1.5                # Maximum forward velocity (matching ROBOT_SPEED)

# --- Objective Weights ---
GOAL_WEIGHT = 1.0                     # How much to prioritize moving toward goal (PSO direction)
OBSTACLE_WEIGHT = 2.0                 # How much to avoid obstacles (static + dynamic)
SMOOTHNESS_WEIGHT = 0.3               # Prefer smooth heading changes (less rotation)
EXPLORATION_WEIGHT = 0.2              # Variance in velocity samples for exploration

# --- Collision Avoidance ---
DWA_COLLISION_DISTANCE = 3.0          # Distance threshold for obstacle collision detection
DWA_ROBOT_COLLISION_DISTANCE = 2.5    # Distance threshold for robot collision prediction
DWA_SAFETY_MARGIN = 0.5               # Extra buffer beyond collision threshold

# --- Heading Smoothness ---
DWA_HEADING_HISTORY = 0.7             # Blend current heading with previous (0=no blend, 1=use old)
DWA_MAX_ANGULAR_VELOCITY = 0.3        # Maximum rotation speed (radians/step)

# --- Debugging ---
DEBUG_PHASE3 = False                   # Print DWA evaluation debug info
LOG_NAVIGATION_STATS = False           # Log velocity selection stats each step


# ============================================================================
# PHASE 4: ENVIRONMENT COMPLEXITY (March 29, 2026)
# ============================================================================
# Dynamic obstacles and terrain modifiers for realistic environments

# --- Master Switch ---
ENABLE_PHASE4_ENVIRONMENT = True  # Set to False to disable Phase 4 features

# --- Dynamic Obstacles ---
DYNAMIC_OBSTACLES = True                # Enable moving/rotating obstacles
DYNAMIC_OBSTACLE_COUNT = 3              # Number of dynamic obstacles to spawn
DYNAMIC_OBSTACLE_MIN_SPEED = 0.1        # Min speed for dynamic obstacles (units/step)
DYNAMIC_OBSTACLE_MAX_SPEED = 0.5        # Max speed for dynamic obstacles
DYNAMIC_OBSTACLE_SPAWN_DISTANCE = 50    # Spawn new obstacles at this distance from origin
DYNAMIC_OBSTACLE_DESPAWN_DISTANCE = 100 # Remove obstacles beyond this distance
DYNAMIC_OBSTACLE_ROTATION_SPEED = 0.3   # Rotation speed for rotating obstacles (rad/step)
DYNAMIC_OBSTACLE_PREDICTION_STEPS = 12  # Steps ahead to predict dynamic obstacle position

# --- Terrain System ---
TERRAIN_ENABLED = True                  # Enable terrain zones with properties
TERRAIN_GRID_SIZE = 10                  # Grid cell size for terrain zones
TERRAIN_FRICTION_ZONES = True           # Add friction/mud zones (slow movement)
TERRAIN_FRICTION_FACTOR = 0.6           # Speed multiplier in friction zones (0.6 = 60% speed)
TERRAIN_SLIPPY_ZONES = False            # Add slippery ice zones (reduced steering control)
TERRAIN_SLIPPY_NOISE = 0.2              # Random velocity perturbation in slippery zones
TERRAIN_STEEP_ZONES = False             # Add elevation changes (not fully implemented)

# --- Collision Prediction for Dynamic Obstacles ---
PREDICT_DYNAMIC_COLLISIONS = True       # Predict moving obstacle positions
DYNAMIC_COLLISION_SAFETY_MARGIN = 1.0   # Extra buffer for moving obstacles

# --- Environment Load Balancing ---
ENVIRONMENT_UPDATE_RATE = 5             # Update dynamic obstacles every N steps (for perf)
MAX_CONCURRENT_DYNAMIC_OBSTACLES = 8    # Safety limit to prevent lag

# --- Debugging ---
DEBUG_PHASE4 = False                    # Print dynamic obstacle/terrain debug info
LOG_ENVIRONMENT_EVENTS = False          # Log obstacle spawn/despawn events
VISUALIZE_TERRAIN = False               # Show terrain zones in animation (future)


# ============================================================================
# PHASE 5: ADVANCED FEATURES (Planned - Not Yet Implemented)
# ============================================================================
# These will be added in Phase 5 (April 10+)

ENABLE_PHASE5_ADVANCED = False

ODOMETRY_ERROR_ENABLED = False         # Robot position drift over time
SENSOR_NOISE_ENABLED = False           # Noisy sensor measurements
FORMATION_CONTROL = False              # Robots maintain geometric formation


# ============================================================================
# SUMMARY
# ============================================================================
"""
To use Phase 1 features:
  1. Ensure ENABLE_PHASE1_PHYSICS = True (default)
  2. Configure individual features above (BATTERY_ENABLED, etc.)
  3. Run simulation normally: python animate_swarm.py
  4. Battery status will show in animation overlay

To disable Phase 1 and use legacy physics:
  1. Set ENABLE_PHASE1_PHYSICS = False
  2. All Phase 1 features are internally disabled
  3. Simulation behaves exactly like v2.2

Individual feature toggles:
  - Disable battery only: set BATTERY_ENABLED = False
  - Disable acceleration smoothing: set SMOOTH_ACCELERATION = False
  - Disable motor delay: set MOTOR_RESPONSE_DELAY = 0
  - Combine as needed for testing
"""

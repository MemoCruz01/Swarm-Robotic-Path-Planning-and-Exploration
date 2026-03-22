"""
Configuration settings for Swarm Robotics Simulation
"""

# Environment settings
ENVIRONMENT_WIDTH = 100
ENVIRONMENT_HEIGHT = 100
GRID_RESOLUTION = 1

# Swarm settings
NUM_ROBOTS = 15
ROBOT_SPEED = 2.0
ROBOT_SENSOR_RANGE = 15.0
ROBOT_SIZE = 1.0

# Obstacle Avoidance Settings
MIN_OBSTACLE_DISTANCE = 8.0  # Increased safety buffer to prevent collision
COLLISION_PREDICTION_RANGE = 3.0  # Look ahead distance for collision detection

# PSO Algorithm settings
PSO_ITERATIONS = 500
PSO_W = 0.7298  # Inertia weight
PSO_C1 = 1.49618  # Cognitive parameter
PSO_C2 = 1.49618  # Social parameter

# Obstacle settings
NUM_OBSTACLES = 8
OBSTACLE_MIN_SIZE = 3
OBSTACLE_MAX_SIZE = 8

# Target settings
TARGET_X = 80
TARGET_Y = 80
TARGET_RADIUS = 5

# Simulation Stopping Conditions
STOP_ON_SINGLE_ROBOT = False  # Stop when ANY robot reaches target
STOP_ON_ALL_ROBOTS = False    # Stop when ALL robots reach target
STOP_ON_PERCENTAGE = True     # Stop when X% of robots reach target
TARGET_ROBOT_PERCENTAGE = 100  # % of robots that must reach target (100 = 100%)

# Exploration parameters
EXPLORATION_DECAY = 0.99
MIN_DISTANCE_TO_OBSTACLE = 5.0

# Visualization settings
VISUALIZATION_INTERVAL = 100  # Update visualization every N iterations
SHOW_VELOCITY_VECTORS = True
SHOW_SENSOR_RANGE = False
ANIMATION_SPEED = 100  # matplotlib animation interval in ms

# Simulation settings
RANDOM_SEED = 42
MAX_SIMULATION_TIME = 1000
USE_ANIMATION = True

"""
Swarm Robotics - Path Planning and Exploration Package
"""

from .environment import Environment, Obstacle
from .robot import Robot
from .swarm import RobotSwarm
from .pso import PSO
from .visualization import SwarmVisualizer

__version__ = "1.0.0"
__author__ = "Swarm Robotics Team"

__all__ = [
    'Environment',
    'Obstacle',
    'Robot',
    'RobotSwarm',
    'PSO',
    'SwarmVisualizer'
]

"""
Terrain System - Environmental complexity layer.

Manages terrain zones with various properties:
- Friction zones (mud, sand) - slow movement
- Slippery zones (ice) - reduced steering control  
- Speed modifier zones - terrain-dependent velocity
- Elevation/slope zones - future extension

Uses grid-based spatial indexing for O(1) lookups.

Created: March 29, 2026
Version: 1.0 (Phase 4 - Environment Complexity)
"""

import numpy as np
from config.realism_settings import (
    TERRAIN_GRID_SIZE,
    TERRAIN_FRICTION_ZONES,
    TERRAIN_FRICTION_FACTOR,
    TERRAIN_SLIPPY_ZONES,
    TERRAIN_SLIPPY_NOISE,
    DEBUG_PHASE4,
)


class TerrainZone:
    """
    Represents a single terrain zone with properties.
    """
    
    def __init__(self, x: float, y: float, radius: float, zone_type: str):
        """
        Initialize terrain zone.
        
        Args:
            x, y: Center position
            radius: Zone radius
            zone_type: 'friction', 'slippy', 'elevation', etc.
        """
        self.x = x
        self.y = y
        self.radius = radius
        self.zone_type = zone_type
        
        # Zone-specific properties
        self.friction_factor = TERRAIN_FRICTION_FACTOR if zone_type == 'friction' else 1.0
        self.slip_noise = TERRAIN_SLIPPY_NOISE if zone_type == 'slippy' else 0.0
        self.elevation_change = 0.0
    
    def get_distance(self, x: float, y: float) -> float:
        """Distance from point to zone center."""
        return np.sqrt((x - self.x)**2 + (y - self.y)**2)
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is within zone."""
        return self.get_distance(x, y) <= self.radius
    
    def get_influence(self, x: float, y: float) -> float:
        """
        Get zone influence at point (0-1).
        Maximum influence at center, decreasing to 0 at radius.
        """
        dist = self.get_distance(x, y)
        if dist >= self.radius:
            return 0.0
        # Linear falloff from center
        return 1.0 - (dist / self.radius)


class TerrainSystem:
    """
    Manages terrain zones efficiently using spatial grid.
    """
    
    def __init__(self, width: float, height: float):
        """
        Initialize terrain system.
        
        Args:
            width: Environment width
            height: Environment height
        """
        self.width = width
        self.height = height
        self.zones = []
        
        # Spatial grid for quick zone lookup
        self.grid_size = TERRAIN_GRID_SIZE
        self.grid_cols = int(np.ceil(width / self.grid_size))
        self.grid_rows = int(np.ceil(height / self.grid_size))
        self.grid = [[[] for _ in range(self.grid_cols)] for _ in range(self.grid_rows)]
    
    def add_zone(self, zone: TerrainZone):
        """Add terrain zone to system."""
        self.zones.append(zone)
        
        # Add to grid cells it overlaps
        min_col = max(0, int((zone.x - zone.radius) / self.grid_size))
        max_col = min(self.grid_cols - 1, int((zone.x + zone.radius) / self.grid_size))
        min_row = max(0, int((zone.y - zone.radius) / self.grid_size))
        max_row = min(self.grid_rows - 1, int((zone.y + zone.radius) / self.grid_size))
        
        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                self.grid[row][col].append(zone)
    
    def get_nearby_zones(self, x: float, y: float, max_distance: float = None) -> list:
        """
        Get terrain zones near a position.
        Uses grid for efficient spatial indexing.
        
        Args:
            x, y: Query position
            max_distance: Only return zones within this distance
            
        Returns:
            List of TerrainZone objects (deduplicated)
        """
        if max_distance is None:
            max_distance = self.grid_size * 2
        
        col = int(x / self.grid_size)
        row = int(y / self.grid_size)
        
        # Search neighboring grid cells
        nearby = []
        seen_zones = set()  # Deduplicate zones across grid cells
        search_radius = int(np.ceil(max_distance / self.grid_size)) + 1
        
        for dr in range(-search_radius, search_radius + 1):
            for dc in range(-search_radius, search_radius + 1):
                r = row + dr
                c = col + dc
                if 0 <= r < self.grid_rows and 0 <= c < self.grid_cols:
                    for zone in self.grid[r][c]:
                        zone_id = id(zone)  # Use object id to deduplicate
                        if zone_id not in seen_zones and zone.get_distance(x, y) <= max_distance:
                            nearby.append(zone)
                            seen_zones.add(zone_id)
        
        return nearby
    
    def get_speed_multiplier(self, x: float, y: float) -> float:
        """
        Get speed modifier at position (accounts for all zones).
        
        Args:
            x, y: Robot position
            
        Returns:
            Speed multiplier (0.5 = half speed, 1.0 = normal)
        """
        nearby_zones = self.get_nearby_zones(x, y)
        
        speed_mult = 1.0
        for zone in nearby_zones:
            if zone.zone_type == 'friction':
                influence = zone.get_influence(x, y)
                # Interpolate between normal and friction speed
                zone_speed = zone.friction_factor + (1.0 - influence) * (1.0 - zone.friction_factor)
                speed_mult *= zone_speed
        
        return speed_mult
    
    def get_steering_noise(self, x: float, y: float) -> float:
        """
        Get steering disturbance at position (for slippery zones).
        
        Args:
            x, y: Robot position
            
        Returns:
            Random noise to add to heading (0-1)
        """
        nearby_zones = self.get_nearby_zones(x, y)
        
        max_noise = 0.0
        for zone in nearby_zones:
            if zone.zone_type == 'slippy':
                influence = zone.get_influence(x, y)
                noise = zone.slip_noise * influence
                max_noise = max(max_noise, noise)
        
        if max_noise > 0:
            return np.random.normal(0, max_noise)
        return 0.0
    
    def create_random_terrain(self, num_friction: int = 3, num_slippy: int = 2):
        """
        Create random terrain zones for testing.
        
        Args:
            num_friction: Number of friction zones to create
            num_slippy: Number of slippy zones to create
        """
        # Create friction zones
        if TERRAIN_FRICTION_ZONES:
            for _ in range(num_friction):
                x = np.random.uniform(10, self.width - 10)
                y = np.random.uniform(10, self.height - 10)
                radius = np.random.uniform(8, 15)
                zone = TerrainZone(x, y, radius, 'friction')
                self.add_zone(zone)
        
        # Create slippy zones
        if TERRAIN_SLIPPY_ZONES:
            for _ in range(num_slippy):
                x = np.random.uniform(10, self.width - 10)
                y = np.random.uniform(10, self.height - 10)
                radius = np.random.uniform(6, 12)
                zone = TerrainZone(x, y, radius, 'slippy')
                self.add_zone(zone)
    
    def get_zone_at(self, x: float, y: float, zone_type: str = None) -> list:
        """
        Get all zones containing point.
        
        Args:
            x, y: Query position
            zone_type: Optional filter by type
            
        Returns:
            List of zones at that position
        """
        result = []
        nearby_zones = self.get_nearby_zones(x, y, max_distance=0)
        
        for zone in nearby_zones:
            if zone.contains_point(x, y):
                if zone_type is None or zone.zone_type == zone_type:
                    result.append(zone)
        
        return result
    
    def get_statistics(self) -> dict:
        """Get terrain system statistics."""
        friction_count = sum(1 for z in self.zones if z.zone_type == 'friction')
        slippy_count = sum(1 for z in self.zones if z.zone_type == 'slippy')
        
        return {
            'total_zones': len(self.zones),
            'friction_zones': friction_count,
            'slippy_zones': slippy_count,
            'grid_cells': self.grid_rows * self.grid_cols,
        }

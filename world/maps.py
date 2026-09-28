# MathMon RPG - World Maps Manager
from world.tilemap import TileMap
from data.maps_data import MAPS


class WorldMap:
    """Manages the game world maps."""

    def __init__(self):
        self.maps = {}
        self.current_map_name = None
        self.current_tilemap = None

    def load_map(self, map_name):
        """Load a map by name."""
        if map_name not in self.maps:
            map_data = MAPS[map_name]
            self.maps[map_name] = TileMap(map_data)
        self.current_map_name = map_name
        self.current_tilemap = self.maps[map_name]
        return self.current_tilemap

    def get_map_data(self, map_name=None):
        """Get raw map data."""
        name = map_name or self.current_map_name
        return MAPS.get(name)

    def get_current_tilemap(self):
        """Get current tilemap."""
        return self.current_tilemap

# MathMon RPG - Tilemap Renderer
import pygame
from settings import *
from utils.sprite_generator import SpriteGenerator


class TileMap:
    """Renders tile-based maps."""

    def __init__(self, map_data):
        self.map_data = map_data
        self.tiles = map_data["tiles"]
        self.width = map_data["width"]
        self.height = map_data["height"]
        self.sprite_gen = SpriteGenerator()

        # Pre-render the map surface
        self.surface = pygame.Surface(
            (self.width * TILE_SIZE, self.height * TILE_SIZE)
        )
        self._render_map()

    def _render_map(self):
        """Pre-render the entire map to a surface."""
        for y, row in enumerate(self.tiles):
            for x, tile_id in enumerate(row):
                tile_sprite = self.sprite_gen.get_tile(tile_id)
                self.surface.blit(tile_sprite, (x * TILE_SIZE, y * TILE_SIZE))

    def get_tile_at(self, x, y):
        """Get tile ID at grid position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return TILE_TREE  # Out of bounds = solid

    def is_solid(self, x, y):
        """Check if a tile is solid (can't walk through)."""
        tile = self.get_tile_at(x, y)
        return tile in SOLID_TILES

    def is_encounter_tile(self, x, y):
        """Check if tile can trigger encounters."""
        tile = self.get_tile_at(x, y)
        return tile in ENCOUNTER_TILES

    def get_portal_at(self, x, y):
        """Check if there's a portal at this position."""
        for portal in self.map_data.get("portals", []):
            if portal["x"] == x and portal["y"] == y:
                return portal
        return None

    def draw(self, screen, camera):
        """Draw the map with camera offset."""
        screen.blit(self.surface, camera.apply_rect(
            pygame.Rect(0, 0, self.surface.get_width(), self.surface.get_height())
        ))

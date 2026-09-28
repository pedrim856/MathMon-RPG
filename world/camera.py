# MathMon RPG - Camera System
import pygame
from settings import *


class Camera:
    """Camera that follows the player."""

    def __init__(self, map_width, map_height):
        self.x = 0
        self.y = 0
        self.map_width = map_width * TILE_SIZE
        self.map_height = map_height * TILE_SIZE
        self.target_x = 0
        self.target_y = 0
        self.smoothing = 8.0

    def update(self, target_x, target_y, dt):
        """Update camera position to follow target."""
        # Center on target
        self.target_x = target_x - SCREEN_WIDTH // 2 + TILE_SIZE // 2
        self.target_y = target_y - SCREEN_HEIGHT // 2 + TILE_SIZE // 2

        # Clamp to map bounds
        self.target_x = max(0, min(self.target_x, self.map_width - SCREEN_WIDTH))
        self.target_y = max(0, min(self.target_y, self.map_height - SCREEN_HEIGHT))

        # Smooth follow
        self.x += (self.target_x - self.x) * min(1, self.smoothing * dt)
        self.y += (self.target_y - self.y) * min(1, self.smoothing * dt)

    def snap_to(self, target_x, target_y):
        """Instantly center the camera on a target, clamped to map bounds."""
        self.target_x = target_x - SCREEN_WIDTH // 2 + TILE_SIZE // 2
        self.target_y = target_y - SCREEN_HEIGHT // 2 + TILE_SIZE // 2
        self.x = max(0, min(self.target_x, self.map_width - SCREEN_WIDTH))
        self.y = max(0, min(self.target_y, self.map_height - SCREEN_HEIGHT))

    def apply(self, pos):
        """Apply camera offset to a position."""
        return (pos[0] - int(self.x), pos[1] - int(self.y))

    def apply_rect(self, rect):
        """Apply camera offset to a rect."""
        return pygame.Rect(rect.x - int(self.x), rect.y - int(self.y),
                           rect.width, rect.height)

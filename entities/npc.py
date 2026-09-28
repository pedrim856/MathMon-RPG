# MathMon RPG - NPC Entity
import pygame
from settings import *
from utils.sprite_generator import SpriteGenerator


class NPC:
    """Non-player character in the overworld."""

    def __init__(self, npc_data):
        self.id = npc_data["id"]
        self.npc_type = npc_data["type"]
        self.grid_x = npc_data["x"]
        self.grid_y = npc_data["y"]
        self.dialog = npc_data.get("dialog", ["..."])
        self.gives_starter = npc_data.get("gives_starter", False)

        # Sprite
        self.sprite_gen = SpriteGenerator()
        self.sprite = self.sprite_gen.get_npc_sprite(self.npc_type)

    def draw(self, screen, camera):
        """Draw the NPC."""
        pos = camera.apply((self.grid_x * TILE_SIZE, self.grid_y * TILE_SIZE))
        screen.blit(self.sprite, pos)

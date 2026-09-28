# MathMon RPG - Player Entity
import pygame
import random
from settings import *
from utils.sprite_generator import SpriteGenerator


class Player:
    """Player character in the overworld."""

    def __init__(self, x, y):
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * TILE_SIZE
        self.pixel_y = y * TILE_SIZE
        self.direction = "down"
        self.moving = False
        self.move_progress = 0
        self.move_speed = 5  # Tiles per second
        self.target_x = x
        self.target_y = y

        # Animation
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_speed = 0.15  # seconds per frame

        # Sprite
        self.sprite_gen = SpriteGenerator()
        self.sprites = self.sprite_gen.get_player_sprites()

        # Step counter for encounters
        self.steps = 0

    def handle_input(self, keys, tilemap, npcs=None, trainers=None):
        """Handle movement input. Returns interaction target or None."""
        if self.moving:
            return None

        dx, dy = 0, 0
        new_dir = self.direction

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
            new_dir = "up"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
            new_dir = "down"
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
            new_dir = "left"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
            new_dir = "right"

        self.direction = new_dir

        if dx != 0 or dy != 0:
            new_x = self.grid_x + dx
            new_y = self.grid_y + dy

            # Check NPC collision
            if npcs:
                for npc in npcs:
                    if npc.grid_x == new_x and npc.grid_y == new_y:
                        return None  # Can't walk into NPC

            # Check trainer collision
            if trainers:
                for trainer in trainers:
                    if trainer.get("x") == new_x and trainer.get("y") == new_y:
                        return None

            # Check tile collision
            if not tilemap.is_solid(new_x, new_y):
                self.target_x = new_x
                self.target_y = new_y
                self.moving = True
                self.move_progress = 0
                return None

        return None

    def check_interaction(self, tilemap, npcs=None, trainers_on_map=None):
        """Check for interaction with facing tile. Returns target or None."""
        dx, dy = 0, 0
        if self.direction == "up":
            dy = -1
        elif self.direction == "down":
            dy = 1
        elif self.direction == "left":
            dx = -1
        elif self.direction == "right":
            dx = 1

        target_x = self.grid_x + dx
        target_y = self.grid_y + dy

        # Check NPCs
        if npcs:
            for npc in npcs:
                if npc.grid_x == target_x and npc.grid_y == target_y:
                    return {"type": "npc", "npc": npc}

        # Check trainers
        if trainers_on_map:
            for trainer_data in trainers_on_map:
                if trainer_data.get("x") == target_x and trainer_data.get("y") == target_y:
                    return {"type": "trainer", "trainer": trainer_data}

        # Check signs
        tile = tilemap.get_tile_at(target_x, target_y)
        if tile == TILE_SIGN:
            return {"type": "sign"}

        return None

    def update(self, dt):
        """Update player position and animation."""
        if self.moving:
            self.move_progress += self.move_speed * dt
            if self.move_progress >= 1.0:
                self.move_progress = 1.0
                self.grid_x = self.target_x
                self.grid_y = self.target_y
                self.pixel_x = self.grid_x * TILE_SIZE
                self.pixel_y = self.grid_y * TILE_SIZE
                self.moving = False
                self.steps += 1
            else:
                # Interpolate position
                self.pixel_x = int(
                    (self.grid_x + (self.target_x - self.grid_x) * self.move_progress) * TILE_SIZE
                )
                self.pixel_y = int(
                    (self.grid_y + (self.target_y - self.grid_y) * self.move_progress) * TILE_SIZE
                )

        # Animation
        if self.moving:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_frame = (self.anim_frame + 1) % 4
        else:
            self.anim_frame = 0
            self.anim_timer = 0

    def check_encounter(self, tilemap):
        """Check if a wild encounter should happen. Returns True if encounter."""
        if tilemap.is_encounter_tile(self.grid_x, self.grid_y):
            return random.random() < ENCOUNTER_CHANCE
        return False

    def check_portal(self, tilemap):
        """Check if player is on a portal. Returns portal data or None."""
        return tilemap.get_portal_at(self.grid_x, self.grid_y)

    def draw(self, screen, camera):
        """Draw the player."""
        sprite = self.sprites[self.direction][self.anim_frame]
        pos = camera.apply((self.pixel_x, self.pixel_y))
        screen.blit(sprite, pos)

    def set_position(self, x, y):
        """Teleport player to grid position."""
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * TILE_SIZE
        self.pixel_y = y * TILE_SIZE
        self.target_x = x
        self.target_y = y
        self.moving = False

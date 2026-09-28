# MathMon RPG - Sprite Generator
# Generates all game sprites programmatically using pygame.draw
import pygame
import math
from settings import *


class SpriteGenerator:
    """Generates all game sprites programmatically."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if SpriteGenerator._initialized:
            return
        SpriteGenerator._initialized = True
        self.tile_cache = {}
        self.monster_cache = {}
        self.player_cache = {}
        self.npc_cache = {}
        self.ui_cache = {}

    # ─── TILE SPRITES ───────────────────────────────────────────────

    def get_tile(self, tile_id):
        """Get or generate a tile sprite."""
        if tile_id not in self.tile_cache:
            self.tile_cache[tile_id] = self._generate_tile(tile_id)
        return self.tile_cache[tile_id]

    def _generate_tile(self, tile_id):
        """Generate a tile surface."""
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))

        if tile_id == TILE_GRASS:
            s.fill((72, 160, 72))
            # Small grass details
            for dx, dy in [(4, 4), (12, 8), (20, 6), (8, 20), (24, 22), (16, 16)]:
                pygame.draw.line(s, (60, 140, 60), (dx, dy + 4), (dx, dy), 1)
                pygame.draw.line(s, (60, 140, 60), (dx + 2, dy + 3), (dx + 3, dy), 1)

        elif tile_id == TILE_TALL_GRASS:
            s.fill((72, 160, 72))
            # Taller grass blades
            for dx in range(2, 30, 4):
                h = 8 + (dx * 3) % 5
                color = (40, 130, 50) if dx % 8 < 4 else (50, 145, 55)
                pygame.draw.line(s, color, (dx, TILE_SIZE), (dx - 2, TILE_SIZE - h), 2)
                pygame.draw.line(s, color, (dx, TILE_SIZE), (dx + 2, TILE_SIZE - h - 2), 2)

        elif tile_id == TILE_PATH:
            s.fill((194, 178, 128))
            # Path texture dots
            for dx, dy in [(5, 5), (15, 10), (25, 3), (8, 22), (20, 25), (12, 15)]:
                pygame.draw.circle(s, (180, 164, 114), (dx, dy), 1)

        elif tile_id == TILE_WATER:
            s.fill((50, 120, 220))
            # Water waves
            for y in range(4, 32, 8):
                points = [(0, y)]
                for x in range(0, 33, 4):
                    points.append((x, y + int(math.sin(x * 0.5) * 2)))
                if len(points) > 1:
                    pygame.draw.lines(s, (80, 150, 240), False, points, 1)

        elif tile_id == TILE_TREE:
            s.fill((72, 160, 72))
            # Trunk
            pygame.draw.rect(s, (120, 80, 40), (12, 18, 8, 14))
            # Canopy (layered circles)
            pygame.draw.circle(s, (30, 110, 40), (16, 12), 12)
            pygame.draw.circle(s, (40, 130, 50), (12, 10), 8)
            pygame.draw.circle(s, (40, 130, 50), (20, 10), 8)
            pygame.draw.circle(s, (50, 145, 55), (16, 8), 7)

        elif tile_id == TILE_ROCK:
            s.fill((72, 160, 72))
            # Rock body
            pygame.draw.polygon(s, (130, 130, 140),
                                [(6, 28), (2, 18), (8, 8), (24, 6), (30, 16), (28, 28)])
            pygame.draw.polygon(s, (150, 150, 160),
                                [(8, 26), (6, 16), (12, 10), (22, 8), (26, 16), (24, 26)])
            # Highlight
            pygame.draw.line(s, (170, 170, 180), (12, 12), (20, 10), 2)

        elif tile_id == TILE_HOUSE:
            s.fill((72, 160, 72))
            # House body
            pygame.draw.rect(s, (180, 120, 80), (2, 12, 28, 20))
            # Roof
            pygame.draw.polygon(s, (180, 50, 40), [(0, 14), (16, 2), (32, 14)])
            pygame.draw.polygon(s, (200, 60, 45), [(2, 13), (16, 3), (30, 13)])
            # Window
            pygame.draw.rect(s, (150, 200, 255), (6, 16, 6, 6))
            pygame.draw.rect(s, (100, 80, 60), (6, 16, 6, 6), 1)
            pygame.draw.line(s, (100, 80, 60), (9, 16), (9, 22), 1)

        elif tile_id == TILE_DOOR:
            s.fill((72, 160, 72))
            # House body
            pygame.draw.rect(s, (180, 120, 80), (2, 12, 28, 20))
            # Roof
            pygame.draw.polygon(s, (180, 50, 40), [(0, 14), (16, 2), (32, 14)])
            # Door
            pygame.draw.rect(s, (100, 60, 30), (11, 17, 10, 15))
            pygame.draw.rect(s, (80, 50, 25), (11, 17, 10, 15), 1)
            pygame.draw.circle(s, (200, 180, 50), (19, 26), 2)

        elif tile_id == TILE_SAND:
            s.fill((220, 200, 140))
            for dx, dy in [(5, 5), (15, 10), (25, 3), (8, 22), (20, 25)]:
                pygame.draw.circle(s, (210, 190, 130), (dx, dy), 1)

        elif tile_id == TILE_CAVE_FLOOR:
            s.fill((80, 70, 60))
            for dx, dy in [(5, 5), (15, 10), (25, 3), (8, 22), (20, 25), (12, 15)]:
                pygame.draw.circle(s, (70, 60, 50), (dx, dy), 2)

        elif tile_id == TILE_CAVE_WALL:
            s.fill((50, 45, 40))
            pygame.draw.rect(s, (60, 55, 48), (2, 2, 28, 28))
            # Cracks
            pygame.draw.line(s, (40, 35, 30), (5, 5), (12, 15), 1)
            pygame.draw.line(s, (40, 35, 30), (20, 8), (25, 20), 1)

        elif tile_id == TILE_PORTAL:
            s.fill((72, 160, 72))
            # Glowing portal
            pygame.draw.circle(s, (100, 50, 150), (16, 16), 12)
            pygame.draw.circle(s, (140, 80, 200), (16, 16), 9)
            pygame.draw.circle(s, (180, 120, 240), (16, 16), 6)
            pygame.draw.circle(s, (220, 180, 255), (16, 16), 3)

        elif tile_id == TILE_SIGN:
            s.fill((72, 160, 72))
            # Sign post
            pygame.draw.rect(s, (139, 90, 43), (14, 14, 4, 18))
            pygame.draw.rect(s, (180, 140, 80), (6, 6, 20, 12))
            pygame.draw.rect(s, (139, 90, 43), (6, 6, 20, 12), 1)
            # Text lines
            pygame.draw.line(s, (100, 60, 30), (9, 10), (23, 10), 1)
            pygame.draw.line(s, (100, 60, 30), (9, 14), (20, 14), 1)

        elif tile_id == TILE_FLOWER:
            s.fill((72, 160, 72))
            # Flowers
            colors = [(255, 100, 100), (255, 200, 50), (200, 100, 255), (255, 150, 180)]
            positions = [(8, 8), (22, 6), (6, 22), (24, 20), (14, 16)]
            for i, (fx, fy) in enumerate(positions):
                c = colors[i % len(colors)]
                pygame.draw.circle(s, c, (fx, fy), 3)
                pygame.draw.circle(s, (255, 255, 100), (fx, fy), 1)

        elif tile_id == TILE_FENCE:
            s.fill((72, 160, 72))
            # Fence posts
            pygame.draw.rect(s, (160, 120, 60), (2, 8, 4, 24))
            pygame.draw.rect(s, (160, 120, 60), (26, 8, 4, 24))
            # Rails
            pygame.draw.rect(s, (180, 140, 70), (2, 12, 28, 3))
            pygame.draw.rect(s, (180, 140, 70), (2, 22, 28, 3))

        elif tile_id == TILE_ARENA_FLOOR:
            s.fill((160, 140, 120))
            # Arena pattern
            pygame.draw.rect(s, (150, 130, 110), (0, 0, 32, 32), 1)
            if (hash(tile_id) % 2) == 0:
                pygame.draw.line(s, (140, 120, 100), (0, 0), (32, 32), 1)

        else:
            s.fill((255, 0, 255))  # Missing tile = magenta

        return s

    # ─── PLAYER SPRITES ─────────────────────────────────────────────

    def get_player_sprites(self):
        """Get player sprites for all directions and animation frames."""
        if not self.player_cache:
            self._generate_player_sprites()
        return self.player_cache

    def _generate_player_sprites(self):
        """Generate player character sprites."""
        # Directions: down=0, left=1, right=2, up=3
        directions = ["down", "left", "right", "up"]
        for d_idx, direction in enumerate(directions):
            frames = []
            for frame in range(4):
                s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                self._draw_character(s, direction, frame,
                                     body_color=(38, 92, 156),
                                     hair_color=(34, 28, 42),
                                     skin_color=(238, 190, 148),
                                     hat_color=(236, 92, 58))
                frames.append(s)
            self.player_cache[direction] = frames

    def _draw_character(self, surface, direction, frame, body_color, hair_color, skin_color,
                        hat_color=None):
        """Draw a character sprite."""
        cx, cy = 16, 16
        # Walking offset
        leg_offset = [0, -1, 0, 1][frame]

        # Shadow
        pygame.draw.ellipse(surface, (0, 0, 0, 60), (6, 26, 20, 6))

        if direction == "down":
            # Body
            pygame.draw.rect(surface, body_color, (9, 14, 14, 12), border_radius=2)
            # Head
            pygame.draw.ellipse(surface, skin_color, (8, 3, 16, 14))
            # Hair
            pygame.draw.ellipse(surface, hair_color, (7, 2, 18, 10))
            # Eyes
            pygame.draw.circle(surface, (40, 40, 40), (12, 10), 2)
            pygame.draw.circle(surface, (40, 40, 40), (20, 10), 2)
            pygame.draw.circle(surface, WHITE, (13, 9), 1)
            pygame.draw.circle(surface, WHITE, (21, 9), 1)
            # Mouth
            pygame.draw.line(surface, (180, 100, 100), (14, 14), (18, 14), 1)
            # Legs
            pygame.draw.rect(surface, (40, 40, 80), (10, 26, 5, 6), border_radius=1)
            pygame.draw.rect(surface, (40, 40, 80), (17, 26, 5, 6), border_radius=1)
            if frame % 2 == 1:
                pygame.draw.rect(surface, (40, 40, 80), (10 + leg_offset, 26, 5, 6), border_radius=1)
            # Hat (red cap like Pokemon trainer)
            if hat_color is None:
                hat_color = (220, 50, 50)
            pygame.draw.ellipse(surface, hat_color, (6, 1, 20, 8))
            pygame.draw.rect(surface, hat_color, (6, 4, 20, 3))
            # Cap brim
            pygame.draw.rect(surface, (180, 40, 40), (5, 6, 22, 3))

        elif direction == "up":
            # Body
            pygame.draw.rect(surface, body_color, (9, 14, 14, 12))
            # Head
            pygame.draw.ellipse(surface, skin_color, (8, 3, 16, 14))
            # Hair (covers more from back)
            pygame.draw.ellipse(surface, hair_color, (7, 2, 18, 12))
            # Legs
            pygame.draw.rect(surface, (40, 40, 80), (10, 26, 5, 6))
            pygame.draw.rect(surface, (40, 40, 80), (17, 26, 5, 6))
            if frame % 2 == 1:
                pygame.draw.rect(surface, (40, 40, 80), (17 - leg_offset, 26, 5, 6))
            # Hat
            if hat_color is None:
                hat_color = (220, 50, 50)
            pygame.draw.ellipse(surface, hat_color, (6, 0, 20, 10))

        elif direction == "left":
            # Body
            pygame.draw.rect(surface, body_color, (10, 14, 12, 12))
            # Head
            pygame.draw.ellipse(surface, skin_color, (8, 3, 14, 14))
            # Hair
            pygame.draw.ellipse(surface, hair_color, (9, 2, 14, 10))
            # Eye
            pygame.draw.circle(surface, (40, 40, 40), (12, 10), 2)
            pygame.draw.circle(surface, WHITE, (11, 9), 1)
            # Legs
            pygame.draw.rect(surface, (40, 40, 80), (11, 26, 5, 6))
            pygame.draw.rect(surface, (40, 40, 80), (17, 26, 5, 6))
            if frame % 2 == 1:
                pygame.draw.rect(surface, (40, 40, 80), (11 + leg_offset, 26, 5, 6))
            # Hat
            if hat_color is None:
                hat_color = (220, 50, 50)
            pygame.draw.ellipse(surface, hat_color, (5, 1, 16, 8))
            pygame.draw.rect(surface, (180, 40, 40), (4, 5, 10, 3))

        elif direction == "right":
            # Body
            pygame.draw.rect(surface, body_color, (10, 14, 12, 12))
            # Head
            pygame.draw.ellipse(surface, skin_color, (10, 3, 14, 14))
            # Hair
            pygame.draw.ellipse(surface, hair_color, (9, 2, 14, 10))
            # Eye
            pygame.draw.circle(surface, (40, 40, 40), (20, 10), 2)
            pygame.draw.circle(surface, WHITE, (21, 9), 1)
            # Legs
            pygame.draw.rect(surface, (40, 40, 80), (11, 26, 5, 6))
            pygame.draw.rect(surface, (40, 40, 80), (17, 26, 5, 6))
            if frame % 2 == 1:
                pygame.draw.rect(surface, (40, 40, 80), (17 - leg_offset, 26, 5, 6))
            # Hat
            if hat_color is None:
                hat_color = (220, 50, 50)
            pygame.draw.ellipse(surface, hat_color, (11, 1, 16, 8))
            pygame.draw.rect(surface, (180, 40, 40), (18, 5, 10, 3))

    # ─── NPC SPRITES ─────────────────────────────────────────────────

    def get_npc_sprite(self, npc_type="professor"):
        """Get NPC sprite."""
        if npc_type not in self.npc_cache:
            self.npc_cache[npc_type] = self._generate_npc(npc_type)
        return self.npc_cache[npc_type]

    def _generate_npc(self, npc_type):
        """Generate NPC sprite."""
        s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)

        if npc_type == "professor":
            self._draw_character(s, "down", 0,
                                 body_color=(240, 240, 240),
                                 hair_color=(200, 200, 200),
                                 skin_color=(240, 200, 160),
                                 hat_color=None)
            # Lab coat effect - white overlay on body
            pygame.draw.rect(s, (240, 240, 240), (9, 14, 14, 12))
            # Glasses
            pygame.draw.circle(s, (200, 200, 200), (12, 10), 3, 1)
            pygame.draw.circle(s, (200, 200, 200), (20, 10), 3, 1)
            pygame.draw.line(s, (200, 200, 200), (15, 10), (17, 10), 1)

        elif npc_type == "trainer":
            self._draw_character(s, "down", 0,
                                 body_color=(200, 60, 60),
                                 hair_color=(30, 30, 30),
                                 skin_color=(220, 180, 140),
                                 hat_color=(30, 30, 30))

        elif npc_type == "girl":
            self._draw_character(s, "down", 0,
                                 body_color=(255, 150, 180),
                                 hair_color=(200, 150, 50),
                                 skin_color=(240, 210, 180),
                                 hat_color=(255, 180, 200))

        elif npc_type == "elder":
            self._draw_character(s, "down", 0,
                                 body_color=(100, 80, 60),
                                 hair_color=(220, 220, 220),
                                 skin_color=(220, 180, 140),
                                 hat_color=(80, 60, 40))

        elif npc_type == "rival":
            self._draw_character(s, "down", 0,
                                 body_color=(60, 60, 160),
                                 hair_color=(100, 60, 30),
                                 skin_color=(240, 200, 160),
                                 hat_color=(60, 60, 160))

        elif npc_type == "boss":
            self._draw_character(s, "down", 0,
                                 body_color=(40, 40, 40),
                                 hair_color=(180, 30, 30),
                                 skin_color=(200, 170, 140),
                                 hat_color=(40, 40, 40))
            # Crown
            pygame.draw.polygon(s, (255, 215, 0),
                                [(8, 4), (10, 0), (13, 3), (16, 0), (19, 3), (22, 0), (24, 4)])

        else:
            self._draw_character(s, "down", 0,
                                 body_color=(100, 150, 100),
                                 hair_color=(60, 50, 40),
                                 skin_color=(240, 200, 160))

        return s

    # ─── MONSTER SPRITES ─────────────────────────────────────────────

    def get_monster_sprite(self, monster_id, size=96, is_shiny=False):
        """Get a monster battle sprite."""
        key = (monster_id, size, is_shiny)
        if key not in self.monster_cache:
            self.monster_cache[key] = self._generate_monster(monster_id, size, is_shiny)
        return self.monster_cache[key]

    def _generate_monster(self, monster_id, size, is_shiny):
        """Generate a monster battle sprite."""
        s = pygame.Surface((size, size), pygame.SRCALPHA)

        monsters = {
            # Fire line
            "flamix": self._draw_flamix,
            "ignidor": self._draw_ignidor,
            "vulcanox": self._draw_vulcanox,
            # Water line
            "aquiel": self._draw_aquiel,
            "tsunark": self._draw_tsunark,
            "leviathor": self._draw_leviathor,
            # Plant line
            "folhex": self._draw_folhex,
            "vineclaw": self._draw_vineclaw,
            "thorndra": self._draw_thorndra,
            # Electric line
            "sparkz": self._draw_sparkz,
            "voltiger": self._draw_voltiger,
            "thundrex": self._draw_thundrex,
        }

        draw_func = monsters.get(monster_id, self._draw_flamix)
        draw_func(s, size)

        if is_shiny:
            # Apply a gold/purple tint by blending
            tint = pygame.Surface((size, size), pygame.SRCALPHA)
            # Fill with a yellowish tint with alpha 255 (to keep opacity) but keeping RGB to multiply
            tint.fill((255, 210, 100, 255))
            s.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        alpha_mask = pygame.mask.from_surface(s)
        outline = alpha_mask.outline()
        if outline:
            outlined = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.lines(outlined, (24, 28, 42, 255), True, outline, max(2, size // 32))
            outlined.blit(s, (0, 0))
            s = outlined

        shadow = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (20, 25, 35, 90),
                            (size * 0.16, size * 0.77, size * 0.68, size * 0.12))
        shadow.blit(s, (0, 0))
        return shadow

    def _draw_flamix(self, s, size):
        """Small fire lizard."""
        cx, cy = size // 2, size // 2 + 10
        # Body
        pygame.draw.ellipse(s, (255, 120, 60), (cx - 18, cy - 12, 36, 28))
        # Head
        pygame.draw.circle(s, (255, 140, 70), (cx, cy - 22), 16)
        # Eyes
        pygame.draw.circle(s, WHITE, (cx - 6, cy - 24), 5)
        pygame.draw.circle(s, WHITE, (cx + 6, cy - 24), 5)
        pygame.draw.circle(s, (40, 40, 40), (cx - 5, cy - 24), 3)
        pygame.draw.circle(s, (40, 40, 40), (cx + 7, cy - 24), 3)
        # Tail flame
        pygame.draw.polygon(s, (255, 200, 50),
                            [(cx + 18, cy), (cx + 30, cy - 15), (cx + 25, cy + 5)])
        pygame.draw.polygon(s, (255, 100, 30),
                            [(cx + 18, cy), (cx + 28, cy - 10), (cx + 23, cy + 3)])
        # Belly
        pygame.draw.ellipse(s, (255, 200, 150), (cx - 10, cy - 4, 20, 16))
        # Legs
        pygame.draw.ellipse(s, (255, 110, 50), (cx - 16, cy + 10, 10, 8))
        pygame.draw.ellipse(s, (255, 110, 50), (cx + 6, cy + 10, 10, 8))

    def _draw_ignidor(self, s, size):
        """Medium fire creature."""
        cx, cy = size // 2, size // 2 + 5
        # Body
        pygame.draw.ellipse(s, (230, 80, 40), (cx - 24, cy - 15, 48, 35))
        # Head
        pygame.draw.circle(s, (240, 90, 45), (cx, cy - 28), 20)
        # Horn
        pygame.draw.polygon(s, (200, 60, 30),
                            [(cx - 8, cy - 44), (cx - 3, cy - 32), (cx - 12, cy - 32)])
        pygame.draw.polygon(s, (200, 60, 30),
                            [(cx + 8, cy - 44), (cx + 3, cy - 32), (cx + 12, cy - 32)])
        # Eyes (fierce)
        pygame.draw.polygon(s, WHITE,
                            [(cx - 12, cy - 30), (cx - 2, cy - 30), (cx - 7, cy - 26)])
        pygame.draw.polygon(s, WHITE,
                            [(cx + 2, cy - 30), (cx + 12, cy - 30), (cx + 7, cy - 26)])
        pygame.draw.circle(s, (200, 30, 30), (cx - 7, cy - 29), 2)
        pygame.draw.circle(s, (200, 30, 30), (cx + 7, cy - 29), 2)
        # Belly
        pygame.draw.ellipse(s, (255, 180, 120), (cx - 14, cy - 5, 28, 22))
        # Arms
        pygame.draw.ellipse(s, (220, 70, 35), (cx - 30, cy - 10, 14, 20))
        pygame.draw.ellipse(s, (220, 70, 35), (cx + 16, cy - 10, 14, 20))
        # Tail
        pygame.draw.polygon(s, (255, 160, 30),
                            [(cx + 22, cy + 5), (cx + 38, cy - 20), (cx + 35, cy + 10)])
        pygame.draw.polygon(s, (255, 220, 50),
                            [(cx + 30, cy - 10), (cx + 42, cy - 25), (cx + 38, cy - 5)])

    def _draw_vulcanox(self, s, size):
        """Large fire dragon."""
        cx, cy = size // 2, size // 2 + 8
        # Wings
        pygame.draw.polygon(s, (200, 60, 30),
                            [(cx - 15, cy - 20), (cx - 45, cy - 40), (cx - 35, cy)])
        pygame.draw.polygon(s, (200, 60, 30),
                            [(cx + 15, cy - 20), (cx + 45, cy - 40), (cx + 35, cy)])
        pygame.draw.polygon(s, (230, 80, 40),
                            [(cx - 12, cy - 18), (cx - 38, cy - 35), (cx - 30, cy - 2)])
        pygame.draw.polygon(s, (230, 80, 40),
                            [(cx + 12, cy - 18), (cx + 38, cy - 35), (cx + 30, cy - 2)])
        # Body
        pygame.draw.ellipse(s, (210, 50, 25), (cx - 25, cy - 15, 50, 38))
        # Head
        pygame.draw.circle(s, (220, 60, 30), (cx, cy - 30), 22)
        # Horns
        pygame.draw.polygon(s, (150, 40, 20),
                            [(cx - 15, cy - 48), (cx - 8, cy - 35), (cx - 18, cy - 35)])
        pygame.draw.polygon(s, (150, 40, 20),
                            [(cx + 15, cy - 48), (cx + 8, cy - 35), (cx + 18, cy - 35)])
        # Eyes (glowing)
        pygame.draw.circle(s, (255, 255, 100), (cx - 8, cy - 32), 5)
        pygame.draw.circle(s, (255, 255, 100), (cx + 8, cy - 32), 5)
        pygame.draw.circle(s, (255, 50, 0), (cx - 8, cy - 32), 3)
        pygame.draw.circle(s, (255, 50, 0), (cx + 8, cy - 32), 3)
        # Mouth
        pygame.draw.line(s, (100, 20, 10), (cx - 10, cy - 20), (cx + 10, cy - 20), 2)
        # Belly
        pygame.draw.ellipse(s, (255, 160, 80), (cx - 16, cy - 5, 32, 24))
        # Tail
        pygame.draw.polygon(s, (255, 100, 20),
                            [(cx + 23, cy + 10), (cx + 45, cy - 5), (cx + 40, cy + 15)])
        pygame.draw.polygon(s, (255, 200, 50),
                            [(cx + 38, cy), (cx + 48, cy - 10), (cx + 45, cy + 8)])

    def _draw_aquiel(self, s, size):
        """Small water creature."""
        cx, cy = size // 2, size // 2 + 8
        # Body
        pygame.draw.ellipse(s, (70, 150, 255), (cx - 18, cy - 14, 36, 30))
        # Head
        pygame.draw.circle(s, (90, 170, 255), (cx, cy - 22), 16)
        # Eyes (big cute)
        pygame.draw.circle(s, WHITE, (cx - 6, cy - 24), 6)
        pygame.draw.circle(s, WHITE, (cx + 6, cy - 24), 6)
        pygame.draw.circle(s, (30, 50, 150), (cx - 5, cy - 24), 3)
        pygame.draw.circle(s, (30, 50, 150), (cx + 7, cy - 24), 3)
        pygame.draw.circle(s, WHITE, (cx - 4, cy - 25), 1)
        pygame.draw.circle(s, WHITE, (cx + 8, cy - 25), 1)
        # Fin on head
        pygame.draw.polygon(s, (50, 120, 220),
                            [(cx, cy - 36), (cx + 5, cy - 28), (cx - 5, cy - 28)])
        # Tail
        pygame.draw.ellipse(s, (60, 140, 240), (cx + 14, cy - 5, 16, 10))
        # Belly
        pygame.draw.ellipse(s, (180, 220, 255), (cx - 10, cy - 4, 20, 16))
        # Flippers
        pygame.draw.ellipse(s, (60, 130, 230), (cx - 22, cy - 8, 10, 14))
        pygame.draw.ellipse(s, (60, 130, 230), (cx + 12, cy - 8, 10, 14))

    def _draw_tsunark(self, s, size):
        """Medium water creature."""
        cx, cy = size // 2, size // 2 + 5
        # Body
        pygame.draw.ellipse(s, (40, 120, 230), (cx - 25, cy - 15, 50, 35))
        # Head
        pygame.draw.circle(s, (50, 130, 240), (cx, cy - 26), 20)
        # Jaw
        pygame.draw.ellipse(s, (40, 110, 220), (cx - 12, cy - 18, 24, 12))
        # Eyes
        pygame.draw.circle(s, WHITE, (cx - 8, cy - 30), 5)
        pygame.draw.circle(s, WHITE, (cx + 8, cy - 30), 5)
        pygame.draw.circle(s, (20, 40, 120), (cx - 7, cy - 30), 3)
        pygame.draw.circle(s, (20, 40, 120), (cx + 9, cy - 30), 3)
        # Fin
        pygame.draw.polygon(s, (30, 100, 200),
                            [(cx, cy - 44), (cx + 8, cy - 28), (cx - 8, cy - 28)])
        # Side fins
        pygame.draw.polygon(s, (30, 100, 200),
                            [(cx - 25, cy - 5), (cx - 38, cy - 18), (cx - 28, cy + 5)])
        pygame.draw.polygon(s, (30, 100, 200),
                            [(cx + 25, cy - 5), (cx + 38, cy - 18), (cx + 28, cy + 5)])
        # Belly
        pygame.draw.ellipse(s, (150, 200, 255), (cx - 14, cy - 5, 28, 22))
        # Teeth
        for i in range(-8, 9, 4):
            pygame.draw.polygon(s, WHITE,
                                [(cx + i, cy - 14), (cx + i + 2, cy - 14), (cx + i + 1, cy - 11)])

    def _draw_leviathor(self, s, size):
        """Large water sea serpent."""
        cx, cy = size // 2, size // 2 + 5
        # Coils
        pygame.draw.ellipse(s, (30, 90, 200), (cx - 30, cy + 5, 25, 20))
        pygame.draw.ellipse(s, (30, 90, 200), (cx + 5, cy + 5, 25, 20))
        # Body
        pygame.draw.ellipse(s, (35, 100, 210), (cx - 28, cy - 15, 56, 35))
        # Head
        pygame.draw.circle(s, (40, 110, 220), (cx, cy - 28), 24)
        # Crown/crest
        for i in range(-2, 3):
            pygame.draw.polygon(s, (100, 200, 255),
                                [(cx + i * 8, cy - 50), (cx + i * 8 + 4, cy - 38),
                                 (cx + i * 8 - 4, cy - 38)])
        # Eyes (piercing)
        pygame.draw.circle(s, (200, 240, 255), (cx - 10, cy - 32), 6)
        pygame.draw.circle(s, (200, 240, 255), (cx + 10, cy - 32), 6)
        pygame.draw.circle(s, (10, 30, 100), (cx - 9, cy - 32), 3)
        pygame.draw.circle(s, (10, 30, 100), (cx + 11, cy - 32), 3)
        # Whiskers
        pygame.draw.line(s, (100, 180, 255), (cx - 20, cy - 22), (cx - 38, cy - 30), 2)
        pygame.draw.line(s, (100, 180, 255), (cx + 20, cy - 22), (cx + 38, cy - 30), 2)
        # Belly scales
        pygame.draw.ellipse(s, (120, 190, 255), (cx - 16, cy - 6, 32, 22))

    def _draw_folhex(self, s, size):
        """Small plant creature."""
        cx, cy = size // 2, size // 2 + 8
        # Body
        pygame.draw.ellipse(s, (60, 180, 80), (cx - 16, cy - 12, 32, 28))
        # Head
        pygame.draw.circle(s, (70, 190, 90), (cx, cy - 20), 15)
        # Leaf on head
        pygame.draw.ellipse(s, (40, 160, 50), (cx - 3, cy - 38, 14, 18))
        pygame.draw.line(s, (30, 130, 40), (cx + 4, cy - 36), (cx + 4, cy - 22), 2)
        # Eyes
        pygame.draw.circle(s, WHITE, (cx - 5, cy - 22), 5)
        pygame.draw.circle(s, WHITE, (cx + 5, cy - 22), 5)
        pygame.draw.circle(s, (30, 80, 30), (cx - 4, cy - 22), 3)
        pygame.draw.circle(s, (30, 80, 30), (cx + 6, cy - 22), 3)
        # Smile
        pygame.draw.arc(s, (40, 100, 40), (cx - 5, cy - 18, 10, 6), 3.14, 6.28, 1)
        # Feet
        pygame.draw.ellipse(s, (50, 160, 70), (cx - 14, cy + 10, 10, 8))
        pygame.draw.ellipse(s, (50, 160, 70), (cx + 4, cy + 10, 10, 8))
        # Belly
        pygame.draw.ellipse(s, (120, 220, 130), (cx - 8, cy - 4, 16, 14))

    def _draw_vineclaw(self, s, size):
        """Medium plant creature."""
        cx, cy = size // 2, size // 2 + 5
        # Vines
        pygame.draw.arc(s, (40, 140, 50), (cx - 40, cy - 20, 30, 40), 0, 3, 3)
        pygame.draw.arc(s, (40, 140, 50), (cx + 10, cy - 20, 30, 40), 0, 3, 3)
        # Body
        pygame.draw.ellipse(s, (50, 160, 60), (cx - 22, cy - 15, 44, 35))
        # Head
        pygame.draw.circle(s, (55, 170, 65), (cx, cy - 26), 19)
        # Flower on head
        for angle in range(0, 360, 60):
            rad = math.radians(angle)
            px = cx + int(10 * math.cos(rad))
            py = cy - 40 + int(10 * math.sin(rad))
            pygame.draw.circle(s, (255, 150, 180), (px, py), 5)
        pygame.draw.circle(s, (255, 255, 100), (cx, cy - 40), 4)
        # Eyes
        pygame.draw.circle(s, WHITE, (cx - 7, cy - 28), 5)
        pygame.draw.circle(s, WHITE, (cx + 7, cy - 28), 5)
        pygame.draw.circle(s, (30, 70, 30), (cx - 6, cy - 28), 3)
        pygame.draw.circle(s, (30, 70, 30), (cx + 8, cy - 28), 3)
        # Belly
        pygame.draw.ellipse(s, (100, 200, 110), (cx - 12, cy - 5, 24, 20))
        # Claws
        pygame.draw.polygon(s, (40, 130, 45),
                            [(cx - 22, cy + 5), (cx - 30, cy + 15), (cx - 18, cy + 15)])
        pygame.draw.polygon(s, (40, 130, 45),
                            [(cx + 22, cy + 5), (cx + 30, cy + 15), (cx + 18, cy + 15)])

    def _draw_thorndra(self, s, size):
        """Large plant dragon."""
        cx, cy = size // 2, size // 2 + 5
        # Body
        pygame.draw.ellipse(s, (40, 140, 50), (cx - 28, cy - 15, 56, 38))
        # Head
        pygame.draw.circle(s, (45, 150, 55), (cx, cy - 30), 22)
        # Thorns on back
        for i in range(-3, 4):
            pygame.draw.polygon(s, (30, 100, 35),
                                [(cx + i * 8, cy - 14), (cx + i * 8 + 4, cy - 24),
                                 (cx + i * 8 - 4, cy - 18)])
        # Rose crown
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            px = cx + int(18 * math.cos(rad))
            py = cy - 46 + int(6 * math.sin(rad))
            pygame.draw.circle(s, (220, 50, 80), (px, py), 5)
        pygame.draw.circle(s, (255, 80, 100), (cx, cy - 46), 6)
        # Eyes
        pygame.draw.circle(s, (200, 255, 200), (cx - 9, cy - 34), 6)
        pygame.draw.circle(s, (200, 255, 200), (cx + 9, cy - 34), 6)
        pygame.draw.circle(s, (20, 60, 20), (cx - 8, cy - 34), 3)
        pygame.draw.circle(s, (20, 60, 20), (cx + 10, cy - 34), 3)
        # Belly
        pygame.draw.ellipse(s, (100, 200, 110), (cx - 18, cy - 5, 36, 24))
        # Vine arms
        pygame.draw.arc(s, (35, 120, 40), (cx - 45, cy - 15, 30, 30), 0, 3, 4)
        pygame.draw.arc(s, (35, 120, 40), (cx + 15, cy - 15, 30, 30), 0, 3, 4)
        # Leaf tips on vines
        pygame.draw.ellipse(s, (30, 110, 35), (cx - 46, cy - 18, 12, 8))
        pygame.draw.ellipse(s, (30, 110, 35), (cx + 34, cy - 18, 12, 8))

    def _draw_sparkz(self, s, size):
        """Small electric mouse."""
        cx, cy = size // 2, size // 2 + 8
        # Body
        pygame.draw.ellipse(s, (255, 220, 50), (cx - 16, cy - 12, 32, 28))
        # Head
        pygame.draw.circle(s, (255, 230, 60), (cx, cy - 20), 15)
        # Ears (pointy)
        pygame.draw.polygon(s, (255, 220, 50),
                            [(cx - 12, cy - 30), (cx - 18, cy - 44), (cx - 6, cy - 32)])
        pygame.draw.polygon(s, (255, 220, 50),
                            [(cx + 12, cy - 30), (cx + 18, cy - 44), (cx + 6, cy - 32)])
        # Ear tips (black)
        pygame.draw.polygon(s, (40, 40, 40),
                            [(cx - 14, cy - 36), (cx - 18, cy - 44), (cx - 10, cy - 36)])
        pygame.draw.polygon(s, (40, 40, 40),
                            [(cx + 14, cy - 36), (cx + 18, cy - 44), (cx + 10, cy - 36)])
        # Eyes
        pygame.draw.circle(s, (40, 40, 40), (cx - 5, cy - 22), 4)
        pygame.draw.circle(s, (40, 40, 40), (cx + 5, cy - 22), 4)
        pygame.draw.circle(s, WHITE, (cx - 4, cy - 23), 2)
        pygame.draw.circle(s, WHITE, (cx + 6, cy - 23), 2)
        # Cheeks (red circles)
        pygame.draw.circle(s, (255, 80, 80), (cx - 13, cy - 16), 4)
        pygame.draw.circle(s, (255, 80, 80), (cx + 13, cy - 16), 4)
        # Belly
        pygame.draw.ellipse(s, (255, 240, 150), (cx - 8, cy - 4, 16, 14))
        # Lightning tail
        pygame.draw.polygon(s, (255, 200, 30),
                            [(cx + 14, cy), (cx + 22, cy - 8), (cx + 18, cy - 4),
                             (cx + 30, cy - 15), (cx + 20, cy - 5), (cx + 24, cy - 10),
                             (cx + 16, cy + 2)])

    def _draw_voltiger(self, s, size):
        """Medium electric tiger."""
        cx, cy = size // 2, size // 2 + 5
        # Body
        pygame.draw.ellipse(s, (240, 200, 40), (cx - 24, cy - 15, 48, 35))
        # Head
        pygame.draw.circle(s, (245, 210, 50), (cx, cy - 26), 20)
        # Ears
        pygame.draw.polygon(s, (240, 200, 40),
                            [(cx - 16, cy - 38), (cx - 22, cy - 52), (cx - 10, cy - 40)])
        pygame.draw.polygon(s, (240, 200, 40),
                            [(cx + 16, cy - 38), (cx + 22, cy - 52), (cx + 10, cy - 40)])
        # Stripes
        for y_off in range(-10, 15, 8):
            pygame.draw.line(s, (40, 40, 40), (cx - 18, cy + y_off), (cx - 10, cy + y_off + 4), 2)
            pygame.draw.line(s, (40, 40, 40), (cx + 18, cy + y_off), (cx + 10, cy + y_off + 4), 2)
        # Eyes (fierce)
        pygame.draw.circle(s, WHITE, (cx - 8, cy - 28), 5)
        pygame.draw.circle(s, WHITE, (cx + 8, cy - 28), 5)
        pygame.draw.circle(s, (40, 40, 40), (cx - 7, cy - 28), 3)
        pygame.draw.circle(s, (40, 40, 40), (cx + 9, cy - 28), 3)
        # Fangs
        pygame.draw.polygon(s, WHITE,
                            [(cx - 5, cy - 18), (cx - 3, cy - 13), (cx - 7, cy - 13)])
        pygame.draw.polygon(s, WHITE,
                            [(cx + 5, cy - 18), (cx + 3, cy - 13), (cx + 7, cy - 13)])
        # Belly
        pygame.draw.ellipse(s, (255, 240, 150), (cx - 14, cy - 5, 28, 20))
        # Electric sparks
        spark_color = (255, 255, 100)
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1 = cx + int(28 * math.cos(rad))
            y1 = cy - 10 + int(20 * math.sin(rad))
            x2 = cx + int(34 * math.cos(rad))
            y2 = cy - 10 + int(26 * math.sin(rad))
            pygame.draw.line(s, spark_color, (x1, y1), (x2, y2), 1)

    def _draw_thundrex(self, s, size):
        """Large electric dragon/rex."""
        cx, cy = size // 2, size // 2 + 5
        # Body
        pygame.draw.ellipse(s, (220, 180, 30), (cx - 28, cy - 15, 56, 38))
        # Head
        pygame.draw.circle(s, (230, 190, 35), (cx, cy - 30), 22)
        # Crown of lightning
        for i in range(-2, 3):
            pygame.draw.polygon(s, (255, 255, 100),
                                [(cx + i * 10, cy - 50), (cx + i * 10 + 3, cy - 40),
                                 (cx + i * 10 - 3, cy - 40)])
        # Eyes (electric glow)
        pygame.draw.circle(s, (255, 255, 200), (cx - 9, cy - 34), 6)
        pygame.draw.circle(s, (255, 255, 200), (cx + 9, cy - 34), 6)
        pygame.draw.circle(s, (40, 40, 40), (cx - 8, cy - 34), 3)
        pygame.draw.circle(s, (40, 40, 40), (cx + 10, cy - 34), 3)
        # Stripes
        for y_off in range(-10, 20, 6):
            pygame.draw.line(s, (40, 40, 40),
                             (cx - 24, cy + y_off), (cx - 14, cy + y_off + 3), 3)
            pygame.draw.line(s, (40, 40, 40),
                             (cx + 24, cy + y_off), (cx + 14, cy + y_off + 3), 3)
        # Belly
        pygame.draw.ellipse(s, (255, 240, 150), (cx - 18, cy - 5, 36, 24))
        # Arms
        pygame.draw.ellipse(s, (210, 170, 25), (cx - 36, cy - 10, 16, 22))
        pygame.draw.ellipse(s, (210, 170, 25), (cx + 20, cy - 10, 16, 22))
        # Lightning bolt tail
        points = [(cx + 26, cy + 10), (cx + 34, cy), (cx + 30, cy + 5),
                  (cx + 42, cy - 10), (cx + 36, cy + 2), (cx + 44, cy - 5)]
        pygame.draw.lines(s, (255, 255, 100), False, points, 3)
        # Electric aura
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            x1 = cx + int(32 * math.cos(rad))
            y1 = cy - 5 + int(25 * math.sin(rad))
            x2 = cx + int(38 * math.cos(rad))
            y2 = cy - 5 + int(30 * math.sin(rad))
            pygame.draw.line(s, (255, 255, 150, 100), (x1, y1), (x2, y2), 1)

    # ─── UI ELEMENTS ─────────────────────────────────────────────────

    def get_hp_bar(self, current, maximum, width=120, height=10):
        """Generate an HP bar with glossy finish."""
        s = pygame.Surface((width, height), pygame.SRCALPHA)
        # Background and border
        pygame.draw.rect(s, (20, 20, 25), (0, 0, width, height), border_radius=4)
        pygame.draw.rect(s, (60, 60, 75), (0, 0, width, height), 1, border_radius=4)
        
        # Fill
        ratio = max(0, current / maximum) if maximum > 0 else 0
        fill_width = int((width - 4) * ratio)
        if ratio > 0.5:
            color = HP_GREEN
            highlight = (100, 240, 150)
        elif ratio > 0.25:
            color = HP_YELLOW
            highlight = (255, 230, 100)
        else:
            color = HP_RED
            highlight = (250, 120, 120)
            
        if fill_width > 0:
            # Main color
            pygame.draw.rect(s, color, (2, 2, fill_width, height - 4), border_radius=3)
            # Gloss highlight (top half)
            pygame.draw.rect(s, highlight, (2, 2, fill_width, (height - 4) // 2), border_radius=3)
        return s

    def get_xp_bar(self, current, maximum, width=120, height=6):
        """Generate an XP bar with glossy finish."""
        s = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(s, (20, 20, 25), (0, 0, width, height), border_radius=3)
        pygame.draw.rect(s, (50, 60, 80), (0, 0, width, height), 1, border_radius=3)
        
        ratio = min(1, current / maximum) if maximum > 0 else 0
        fill_width = int((width - 2) * ratio)
        if fill_width > 0:
            pygame.draw.rect(s, XP_BLUE, (1, 1, fill_width, height - 2), border_radius=2)
            # Gloss highlight
            pygame.draw.rect(s, (120, 200, 255), (1, 1, fill_width, (height - 2) // 2), border_radius=2)
        return s

    def get_type_icon(self, element_type, size=20):
        """Generate a type icon."""
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        c = size // 2

        if element_type == "fogo":
            pygame.draw.polygon(s, FIRE_COLOR,
                                [(c, 2), (c + 6, c + 4), (c, c - 1), (c - 6, c + 4)])
            pygame.draw.polygon(s, (255, 200, 80),
                                [(c, 6), (c + 3, c + 2), (c, c), (c - 3, c + 2)])
        elif element_type == "agua":
            pygame.draw.circle(s, WATER_COLOR, (c, c + 2), 7)
            pygame.draw.polygon(s, WATER_COLOR, [(c, 2), (c - 5, c + 2), (c + 5, c + 2)])
        elif element_type == "planta":
            pygame.draw.ellipse(s, PLANT_COLOR, (c - 6, 2, 12, 16))
            pygame.draw.line(s, (40, 130, 50), (c, 4), (c, 16), 2)
        elif element_type == "eletrico":
            pygame.draw.polygon(s, ELECTRIC_COLOR,
                                [(c - 2, 2), (c - 5, c), (c - 1, c), (c - 3, size - 2),
                                 (c + 5, c - 2), (c + 1, c - 2), (c + 2, 2)])
        elif element_type == "terra":
            pygame.draw.polygon(s, TERRA_COLOR, [(c, 2), (c - 8, size - 4), (c + 8, size - 4)])
        elif element_type == "gelo":
            pygame.draw.polygon(s, GELO_COLOR, [(c, 2), (c - 5, c), (c, size - 2), (c + 5, c)])
        elif element_type == "logico":
            pygame.draw.rect(s, LOGICO_COLOR, (c - 4, c - 4, 8, 8))
        elif element_type == "caos":
            pygame.draw.circle(s, CAOS_COLOR, (c, c), 5, 2)
            pygame.draw.line(s, CAOS_COLOR, (c - 6, c - 6), (c + 6, c + 6), 2)
            pygame.draw.line(s, CAOS_COLOR, (c + 6, c - 6), (c - 6, c + 6), 2)

        return s

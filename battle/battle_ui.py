# MathMon RPG - Modern Battle UI
import pygame
import math
import random
import time
from settings import *
from utils.sprite_generator import SpriteGenerator
from data.items_db import ITEMS_DB, BATTLE_ITEMS


def wrap_text(text, font, max_width):
    """Splits text into lines that fit within max_width."""
    if not text:
        return []
    words = text.split(" ")
    lines = []
    current = []
    for word in words:
        test_line = " ".join(current + [word])
        if font.size(test_line)[0] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


class BattleUI:
    """Renders the battle screen with modern aesthetics, animations, and high contrast."""

    # Anchor points for hit effects / damage popups
    ENEMY_HIT_POS = (565, 140)
    PLAYER_HIT_POS = (185, 270)

    # Action buttons metadata
    ACTIONS = [
        {
            "id": "attack",
            "title": "ATACAR",
            "subtitle": "Golpes & Cálculos",
            "icon_type": "attack",
            "color": (245, 75, 75),       # Crimson Red
            "border": (255, 120, 120),
        },
        {
            "id": "defend",
            "title": "DEFENDER",
            "subtitle": "-50% Dano Próx.",
            "icon_type": "defend",
            "color": (55, 135, 255),      # Azure Blue
            "border": (115, 185, 255),
        },
        {
            "id": "item",
            "title": "MOCHILA",
            "subtitle": "Poções & Suporte",
            "icon_type": "item",
            "color": (35, 200, 125),      # Emerald Green
            "border": (90, 240, 170),
        },
        {
            "id": "run",
            "title": "FUGIR",
            "subtitle": "Tentar Escapar",
            "icon_type": "run",
            "color": (250, 165, 35),      # Vibrant Gold
            "border": (255, 210, 95),
        },
    ]

    # Challenge types metadata
    CHALLENGE_META = {
        CHALLENGE_MATH: {
            "label": "MATEMÁTICA",
            "short": "MAT",
            "color": (45, 185, 240),
            "tag_bg": (20, 65, 95),
            "desc": "Resolva o cálculo aritmético para liberar o poder do golpe!",
        },
        CHALLENGE_EQUATION: {
            "label": "EQUAÇÃO",
            "short": "EQUA",
            "color": (175, 95, 250),
            "tag_bg": (60, 30, 95),
            "desc": "Encontre a incógnita X para desferir um golpe crítico!",
        },
        CHALLENGE_MEMORY: {
            "label": "MEMÓRIA",
            "short": "MEM",
            "color": (255, 175, 45),
            "tag_bg": (95, 60, 18),
            "desc": "Memorize a sequência exibida e repita sem errar!",
        },
        CHALLENGE_LOGIC: {
            "label": "LÓGICA",
            "short": "LÓG",
            "color": (45, 205, 125),
            "tag_bg": (18, 75, 42),
            "desc": "Descubra o padrão lógico da sequência para golpear!",
        },
    }

    TYPE_COLORS = {
        "fogo": FIRE_COLOR,
        "agua": WATER_COLOR,
        "planta": PLANT_COLOR,
        "eletrico": ELECTRIC_COLOR,
        "terra": TERRA_COLOR,
        "gelo": GELO_COLOR,
        "logico": LOGICO_COLOR,
        "caos": CAOS_COLOR,
        "normal": (165, 172, 188),
    }

    def __init__(self, game):
        self.game = game
        self.sprite_gen = SpriteGenerator()
        self.fonts = game.fonts

        # Animation state
        self.shake_timer = 0
        self.flash_timer = 0
        self.hit_flash_timer = 0
        self.slide_offset = 0
        self.enemy_slide = 0.0        # 0 -> 1 slide during battle intro
        self.time = 0.0

        # Particles / popups
        self.particles = []
        self.damage_popups = []

        # Smooth HP bars (tween toward real value)
        self._target_hp = {"player": None, "enemy": None}
        self._display_hp = {"player": None, "enemy": None}

        # Menu state
        self.selected_action = 0
        self.selected_move = 0
        self.selected_option = 0
        self.selected_item = 0

        # Challenge UI state
        self.answer_text = ""
        self.timer_display = 0
        self.show_result = False
        self.result_timer = 0
        self.result_correct = False

        # Memory challenge colors
        self.memory_colors_map = {
            "V": (230, 50, 50),
            "Az": (50, 120, 240),
            "Am": (240, 210, 45),
            "Vd": (45, 195, 85),
            "Lj": (245, 140, 30),
            "Rx": (170, 60, 220),
        }

        # Cached click rects for mouse interaction
        self._action_rects = []
        self._move_rects = []
        self._option_rects = []
        self._item_rects = []
        self._back_rect = None

    # ─── DRAWING UTILITIES ──────────────────────────────────────────

    def _get_font(self, name, fallback="medium"):
        """Safely fetch a font or fallback."""
        return self.fonts.get(name, self.fonts.get(fallback))

    def _draw_text_with_shadow(self, screen, text, pos, font, color=WHITE, shadow_color=BLACK, offset=(1, 1)):
        """Draws crisp antialiased text with a soft shadow for high contrast."""
        if not text:
            return None
        shadow_surf = font.render(text, True, shadow_color)
        screen.blit(shadow_surf, (pos[0] + offset[0], pos[1] + offset[1]))
        text_surf = font.render(text, True, color)
        screen.blit(text_surf, pos)
        return text_surf.get_rect(topleft=pos)

    def _draw_text_centered(self, screen, text, rect, font, color=WHITE, shadow_color=BLACK):
        """Draws text centered in a given rectangle with shadow."""
        if not text:
            return
        if shadow_color:
            shadow_surf = font.render(text, True, shadow_color)
            s_rect = shadow_surf.get_rect(center=(rect.centerx + 1, rect.centery + 1))
            screen.blit(shadow_surf, s_rect)
        text_surf = font.render(text, True, color)
        t_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, t_rect)

    def _draw_polygon_arrow(self, screen, x, y, size, color, direction="right"):
        """Draws a crisp geometric arrow indicator without font glyph dependencies."""
        if direction == "right":
            pts = [(x, y - size), (x + int(size * 1.3), y), (x, y + size)]
        elif direction == "down":
            pts = [(x - size, y), (x + size, y), (x, y + int(size * 1.3))]
        elif direction == "up":
            pts = [(x - size, y), (x + size, y), (x, y - int(size * 1.3))]
        else: # left
            pts = [(x, y - size), (x - int(size * 1.3), y), (x, y + size)]
        pygame.draw.polygon(screen, color, pts)

    def _draw_action_icon(self, screen, icon_type, x, y, size=20, color=WHITE):
        """Draws crisp geometric icons for actions without font glyph dependencies."""
        cx = x + size // 2
        cy = y + size // 2
        if icon_type == "attack": # Crossed swords
            s = size // 2
            pygame.draw.line(screen, color, (cx - s + 2, cy - s + 2), (cx + s - 2, cy + s - 2), 3)
            pygame.draw.line(screen, color, (cx - s + 2, cy + s - 2), (cx + s - 2, cy - s + 2), 3)
            pygame.draw.line(screen, (255, 210, 210), (cx - 4, cy - s + 6), (cx - s + 6, cy - 4), 2)
            pygame.draw.line(screen, (255, 210, 210), (cx + 4, cy - s + 6), (cx + s - 6, cy - 4), 2)
        elif icon_type == "defend": # Heraldic shield
            pts = [
                (cx - 7, cy - 8),
                (cx + 7, cy - 8),
                (cx + 7, cy + 2),
                (cx, cy + 9),
                (cx - 7, cy + 2),
            ]
            pygame.draw.polygon(screen, color, pts)
            pygame.draw.line(screen, WHITE, (cx, cy - 6), (cx, cy + 6), 2)
            pygame.draw.line(screen, WHITE, (cx - 5, cy - 2), (cx + 5, cy - 2), 2)
        elif icon_type == "item": # Potion flask
            pygame.draw.rect(screen, color, (cx - 2, cy - 8, 5, 4))
            pygame.draw.rect(screen, (230, 195, 120), (cx - 4, cy - 10, 9, 2))
            pygame.draw.circle(screen, color, (cx, cy + 2), 7)
            pygame.draw.circle(screen, WHITE, (cx - 2, cy), 2)
        elif icon_type == "run": # Double chevrons >>
            pygame.draw.polygon(screen, color, [(cx - 7, cy - 6), (cx - 1, cy), (cx - 7, cy + 6)])
            pygame.draw.polygon(screen, color, [(cx + 1, cy - 6), (cx + 7, cy), (cx + 1, cy + 6)])

    def _draw_panel_background(self, screen, menu_y=BATTLE_PANEL_Y):
        """Draws the solid bottom console deck with glowing top border."""
        deck_rect = pygame.Rect(0, menu_y, SCREEN_WIDTH, SCREEN_HEIGHT - menu_y)
        # 100% OPAQUE base to guarantee zero bleed-through from earlier screens
        pygame.draw.rect(screen, (16, 18, 28), deck_rect)

        # Subtle upper gradient on deck
        grad_surf = pygame.Surface((SCREEN_WIDTH, 40), pygame.SRCALPHA)
        for y in range(40):
            alpha = int(45 * (1.0 - y / 40))
            pygame.draw.line(grad_surf, (40, 60, 95, alpha), (0, y), (SCREEN_WIDTH, y))
        screen.blit(grad_surf, (0, menu_y))

        # Glowing accent border line at the top
        pygame.draw.line(screen, (30, 40, 60), (0, menu_y), (SCREEN_WIDTH, menu_y), 3)
        pygame.draw.line(screen, UI_ACCENT, (0, menu_y), (SCREEN_WIDTH, menu_y), 1)

    # ─── BATTLE SCENE SCENERY & MONSTERS ────────────────────────────

    def draw_battle_scene(self, screen, player_mon, enemy_mon, bg_type="grass"):
        """Draw the battle background scenery, 3D platforms, and monsters."""
        scene_height = BATTLE_PANEL_Y
        scene = pygame.Surface((SCREEN_WIDTH, scene_height))

        # Sky and backdrop gradients
        if bg_type == "cave":
            c_top = (26, 20, 36)
            c_bot = (58, 44, 66)
            accent = (130, 85, 155)
            horizon_y = 230
        elif bg_type == "arena":
            c_top = (95, 55, 48)
            c_bot = (165, 110, 80)
            accent = (225, 180, 95)
            horizon_y = 230
        else: # grass / default
            c_top = (50, 95, 185)     # Deep royal sky
            c_bot = (160, 205, 240)   # Horizon cyan
            accent = (95, 180, 115)
            horizon_y = 225

        # Render sky gradient
        for y in range(horizon_y):
            ratio = y / horizon_y
            r = int(c_top[0] * (1 - ratio) + c_bot[0] * ratio)
            g = int(c_top[1] * (1 - ratio) + c_bot[1] * ratio)
            b = int(c_top[2] * (1 - ratio) + c_bot[2] * ratio)
            pygame.draw.line(scene, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Scenery details
        if bg_type == "grass":
            # Radiant sun
            pygame.draw.circle(scene, (255, 250, 200, 90), (680, 60), 38)
            pygame.draw.circle(scene, (255, 252, 220), (680, 60), 24)
            # Floating clouds
            for cx, cy, cw in [(140, 65, 60), (380, 95, 80), (580, 45, 50)]:
                cloud_x = int(cx + (self.time * 8) % (SCREEN_WIDTH + 100)) - 50
                pygame.draw.ellipse(scene, (235, 245, 255, 210), (cloud_x, cy, cw, 22))
                pygame.draw.ellipse(scene, (255, 255, 255, 230), (cloud_x + 10, cy - 8, cw - 20, 22))
            # Rolling horizon hills
            hill_surf = pygame.Surface((SCREEN_WIDTH, 45), pygame.SRCALPHA)
            pygame.draw.ellipse(hill_surf, (80, 140, 95), (-40, 0, 480, 70))
            pygame.draw.ellipse(hill_surf, (95, 160, 105), (360, 5, 500, 70))
            scene.blit(hill_surf, (0, horizon_y - 28))

            # Ground fill
            ground_top = (85, 165, 95)
            ground_bot = (45, 110, 65)
            for y in range(horizon_y, scene_height):
                ratio = (y - horizon_y) / (scene_height - horizon_y)
                r = int(ground_top[0] * (1 - ratio) + ground_bot[0] * ratio)
                g = int(ground_top[1] * (1 - ratio) + ground_bot[1] * ratio)
                b = int(ground_top[2] * (1 - ratio) + ground_bot[2] * ratio)
                pygame.draw.line(scene, (r, g, b), (0, y), (SCREEN_WIDTH, y))

            # Dynamic swaying grass blades on field
            for x in range(10, SCREEN_WIDTH, 24):
                sway = int(math.sin(self.time * 2.5 + x * 0.1) * 3)
                pygame.draw.line(scene, (115, 190, 125), (x, 260), (x + 6 + sway, 244), 2)
                pygame.draw.line(scene, (135, 210, 145), (x + 3, 260), (x + sway, 242), 1)

        elif bg_type == "cave":
            # Cave ground
            ground_top = (45, 38, 52)
            ground_bot = (28, 22, 34)
            for y in range(horizon_y, scene_height):
                ratio = (y - horizon_y) / (scene_height - horizon_y)
                r = int(ground_top[0] * (1 - ratio) + ground_bot[0] * ratio)
                g = int(ground_top[1] * (1 - ratio) + ground_bot[1] * ratio)
                b = int(ground_top[2] * (1 - ratio) + ground_bot[2] * ratio)
                pygame.draw.line(scene, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            # Stalactites & glowing crystals
            for x, y, r in [(100, 70, 36), (280, 45, 26), (690, 95, 44)]:
                pygame.draw.polygon(scene, (36, 30, 45), [(x - r, 0), (x + r, 0), (x, y)])
                pygame.draw.circle(scene, accent, (x, y - 4), 4)
            # Water drips
            for i, (bx, by) in enumerate([(150, 40), (420, 20), (620, 60)]):
                dy = by + int((self.time * 50 + i * 40) % 90)
                if dy < 210:
                    pygame.draw.circle(scene, (150, 180, 255), (bx, dy), 2)
        else: # Arena
            ground_top = (145, 100, 75)
            ground_bot = (95, 65, 48)
            for y in range(horizon_y, scene_height):
                ratio = (y - horizon_y) / (scene_height - horizon_y)
                r = int(ground_top[0] * (1 - ratio) + ground_bot[0] * ratio)
                g = int(ground_top[1] * (1 - ratio) + ground_bot[1] * ratio)
                b = int(ground_top[2] * (1 - ratio) + ground_bot[2] * ratio)
                pygame.draw.line(scene, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            # Arena spectator banners
            for bx in range(40, 760, 110):
                wave = int(math.sin(self.time * 4 + bx) * 4)
                pygame.draw.polygon(scene, (190, 45, 45),
                                    [(bx, 30), (bx + 26, 30), (bx + 13 + wave, 56)])
                pygame.draw.polygon(scene, (230, 185, 60),
                                    [(bx + 4, 30), (bx + 22, 30), (bx + 13 + wave, 46)])

        # Stage horizon line
        pygame.draw.line(scene, accent, (0, horizon_y), (SCREEN_WIDTH, horizon_y), 2)
        screen.blit(scene, (0, 0))

        # ─── 3D Battle Podiums / Platforms ──────────────────────────
        # Enemy Podium (Top-Right): Center at (565, 180)
        # Player Podium (Bottom-Left): Center at (185, 325)
        platform_surf = pygame.Surface((SCREEN_WIDTH, scene_height), pygame.SRCALPHA)

        # 1. Enemy Podium
        ecx, ecy = 565, 180
        ew, eh = 250, 52
        # Ground cast shadow
        pygame.draw.ellipse(platform_surf, (15, 20, 28, 120), (ecx - ew // 2 - 10, ecy - eh // 2 + 10, ew + 20, eh))
        # 3D Base bevel (depth)
        pygame.draw.ellipse(platform_surf, (40, 85, 60) if bg_type == "grass" else (50, 45, 60),
                            (ecx - ew // 2, ecy - eh // 2 + 6, ew, eh))
        # Upper turf surface
        pygame.draw.ellipse(platform_surf, (75, 155, 90) if bg_type == "grass" else (75, 65, 88),
                            (ecx - ew // 2, ecy - eh // 2, ew, eh))
        # Inner highlight ring
        pygame.draw.ellipse(platform_surf, (110, 195, 120) if bg_type == "grass" else (105, 95, 125),
                            (ecx - ew // 2 + 12, ecy - eh // 2 + 5, ew - 24, eh - 10), 2)

        # 2. Player Podium
        pcx, pcy = 185, 325
        pw, ph = 270, 56
        # Ground cast shadow
        pygame.draw.ellipse(platform_surf, (15, 20, 28, 140), (pcx - pw // 2 - 12, pcy - ph // 2 + 12, pw + 24, ph))
        # 3D Base bevel
        pygame.draw.ellipse(platform_surf, (40, 85, 60) if bg_type == "grass" else (50, 45, 60),
                            (pcx - pw // 2, pcy - ph // 2 + 7, pw, ph))
        # Upper turf surface
        pygame.draw.ellipse(platform_surf, (80, 165, 95) if bg_type == "grass" else (78, 68, 92),
                            (pcx - pw // 2, pcy - ph // 2, pw, ph))
        # Inner highlight ring
        pygame.draw.ellipse(platform_surf, (115, 205, 125) if bg_type == "grass" else (110, 100, 130),
                            (pcx - pw // 2 + 14, pcy - ph // 2 + 5, pw - 28, ph - 10), 2)

        screen.blit(platform_surf, (0, 0))

        # ─── Monster Rendering & Grounding ──────────────────────────
        # Enemy Monster
        enemy_sprite = self.sprite_gen.get_monster_sprite(enemy_mon.monster_id, 96, enemy_mon.is_shiny)
        slide_off = int((1.0 - min(1.0, self.enemy_slide)) * 320)
        enemy_bob = int(math.sin(self.time * 2.8) * 3)

        # Feet aligned to rest naturally on the enemy platform surface (y=175)
        enemy_x = ecx - 48 + slide_off
        enemy_y = 104 + enemy_bob

        if self.shake_timer > 0:
            enemy_x += int(math.sin(self.shake_timer * 35) * 6)

        # Shadow beneath monster on platform
        shadow_w = int(60 * (1.0 - enemy_bob * 0.04))
        pygame.draw.ellipse(screen, (20, 35, 25, 100), (enemy_x + 48 - shadow_w // 2, 172, shadow_w, 14))

        screen.blit(enemy_sprite, (enemy_x, enemy_y))

        # Hit flash on enemy
        if self.hit_flash_timer > 0:
            flash = pygame.Surface(enemy_sprite.get_size(), pygame.SRCALPHA)
            alpha = int(190 * min(1.0, self.hit_flash_timer * 6))
            flash.fill((255, 255, 255, alpha))
            screen.blit(flash, (enemy_x, enemy_y))

        # Player Monster
        player_sprite = self.sprite_gen.get_monster_sprite(player_mon.monster_id, 112, player_mon.is_shiny)
        player_bob = int(math.sin(self.time * 2.8 + 1.4) * 3.5)

        # Feet aligned to rest naturally on player platform surface (y=318)
        player_x = pcx - 56
        player_y = 232 + player_bob

        # Shadow beneath player monster
        pshadow_w = int(72 * (1.0 - player_bob * 0.04))
        pygame.draw.ellipse(screen, (20, 35, 25, 110), (player_x + 56 - pshadow_w // 2, 318, pshadow_w, 16))

        screen.blit(player_sprite, (player_x, player_y))

        # ─── Monster HUD Info Pods ──────────────────────────────────
        # Enemy Info Box: Top-Left (24, 20)
        self._draw_monster_info(screen, enemy_mon, 24, 20, True)

        # Player Info Box: Bottom-Right (480, 265)
        self._draw_monster_info(screen, player_mon, 480, 265, False)

        # Floating damage popups and sparks
        self._draw_popups(screen)

    def _draw_monster_info(self, screen, monster, x, y, is_enemy):
        """Draw a sleek, modern glassmorphism info card with glowing meters."""
        width = 280
        height = 76 if is_enemy else 96

        key = "enemy" if is_enemy else "player"
        display_hp = self._display_hp.get(key)
        if display_hp is None:
            display_hp = monster.current_hp

        # Card drop shadow
        shadow_surf = pygame.Surface((width + 8, height + 8), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 90), (4, 4, width, height), border_radius=12)
        screen.blit(shadow_surf, (x, y))

        # Card body (glassmorphic dark slate)
        card_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (20, 24, 38, 240), (0, 0, width, height), border_radius=12)
        pygame.draw.rect(card_surf, (65, 80, 115), (0, 0, width, height), 2, border_radius=12)

        # Elemental color top strip accent
        m_type = getattr(monster, "type", "normal")
        type_col = self.TYPE_COLORS.get(m_type, UI_ACCENT)
        pygame.draw.rect(card_surf, type_col, (12, 0, width - 24, 3), border_radius=2)
        screen.blit(card_surf, (x, y))

        # Monster Name with crisp shadow for 100% legibility
        name_font = self._get_font("medium_bold", "medium")
        self._draw_text_with_shadow(screen, monster.name, (x + 14, y + 9), name_font, WHITE)

        # Type icon badge
        type_icon = self.sprite_gen.get_type_icon(m_type, 18)
        name_w = name_font.size(monster.name)[0]
        screen.blit(type_icon, (x + 18 + name_w, y + 12))

        # Level badge (golden pill)
        lvl_str = f"Nv.{monster.level}"
        lvl_font = self._get_font("small_bold", "small")
        lvl_w = lvl_font.size(lvl_str)[0] + 16
        lvl_rect = pygame.Rect(x + width - lvl_w - 12, y + 10, lvl_w, 22)
        pygame.draw.rect(screen, (40, 32, 18), lvl_rect, border_radius=6)
        pygame.draw.rect(screen, UI_HIGHLIGHT, lvl_rect, 1, border_radius=6)
        self._draw_text_centered(screen, lvl_str, lvl_rect, lvl_font, UI_HIGHLIGHT, BLACK)

        # ─── HP Bar ─────────────────────────────────────────────────
        hp_x = x + 14
        hp_y = y + 42
        hp_bar_width = 165
        hp_bar_height = 12

        # HP label pill
        hp_label_font = self._get_font("tiny", "small")
        hp_tag_rect = pygame.Rect(hp_x, hp_y - 3, 30, hp_bar_height + 6)
        pygame.draw.rect(screen, (22, 38, 26), hp_tag_rect, border_radius=5)
        pygame.draw.rect(screen, HP_GREEN, hp_tag_rect, 1, border_radius=5)
        self._draw_text_centered(screen, "HP", hp_tag_rect, hp_label_font, HP_GREEN, BLACK)

        # HP trough background
        bar_x = hp_x + 36
        pygame.draw.rect(screen, (14, 16, 22), (bar_x, hp_y, hp_bar_width, hp_bar_height), border_radius=4)
        pygame.draw.rect(screen, (55, 65, 85), (bar_x, hp_y, hp_bar_width, hp_bar_height), 1, border_radius=4)

        # Ratio & Color
        ratio = max(0.0, min(1.0, display_hp / monster.max_hp)) if monster.max_hp > 0 else 0.0
        fill_w = int(hp_bar_width * ratio)

        if ratio > 0.5:
            bar_col = HP_GREEN
            top_col = (110, 240, 160)
        elif ratio > 0.25:
            bar_col = HP_YELLOW
            top_col = (255, 235, 120)
        else:
            bar_col = HP_RED
            top_col = (255, 130, 130)

        if fill_w > 0:
            pygame.draw.rect(screen, bar_col, (bar_x + 1, hp_y + 1, fill_w - 2, hp_bar_height - 2), border_radius=3)
            pygame.draw.rect(screen, top_col, (bar_x + 1, hp_y + 1, fill_w - 2, (hp_bar_height - 2) // 2), border_radius=3)

        # Numeric HP text
        hp_num_str = f"{int(round(display_hp))}/{monster.max_hp}"
        small_font = self._get_font("small")
        self._draw_text_with_shadow(screen, hp_num_str, (bar_x + hp_bar_width + 8, hp_y - 2),
                                    small_font, (240, 245, 250))

        # ─── XP Bar (Player only) ───────────────────────────────────
        if not is_enemy:
            xp_y = y + 68
            xp_width = 185
            xp_height = 8

            xp_tag_rect = pygame.Rect(hp_x, xp_y - 3, 30, xp_height + 6)
            pygame.draw.rect(screen, (20, 30, 48), xp_tag_rect, border_radius=4)
            pygame.draw.rect(screen, XP_BLUE, xp_tag_rect, 1, border_radius=4)
            self._draw_text_centered(screen, "XP", xp_tag_rect, hp_label_font, (90, 200, 255), BLACK)

            # XP trough
            pygame.draw.rect(screen, (14, 16, 22), (bar_x, xp_y, xp_width, xp_height), border_radius=3)
            pygame.draw.rect(screen, (45, 58, 80), (bar_x, xp_y, xp_width, xp_height), 1, border_radius=3)

            xp_needed = max(1, xp_for_level(monster.level))
            xp_ratio = min(1.0, monster.xp / xp_needed) if xp_needed > 0 else 0
            xp_fill = int(xp_width * xp_ratio)

            if xp_fill > 0:
                pygame.draw.rect(screen, XP_BLUE, (bar_x + 1, xp_y + 1, xp_fill - 2, xp_height - 2), border_radius=2)
                pygame.draw.rect(screen, (130, 215, 255), (bar_x + 1, xp_y + 1, xp_fill - 2, (xp_height - 2) // 2), border_radius=2)

            # XP percentage
            xp_pct = f"{int(xp_ratio * 100)}%"
            self._draw_text_with_shadow(screen, xp_pct, (bar_x + xp_width + 8, xp_y - 3),
                                        hp_label_font, (120, 190, 240))

    # ─── ACTION MENU (PLAYER TURN) ──────────────────────────────────

    def draw_action_menu(self, screen, selected):
        """Draw the modernized action console with vibrant, balanced 2x2 cards."""
        menu_y = BATTLE_PANEL_Y
        self._draw_panel_background(screen, menu_y)

        # ─── Left Status / Prompt Deck ───
        deck_rect = pygame.Rect(24, menu_y + 16, 305, 188)
        pygame.draw.rect(screen, (22, 26, 40), deck_rect, border_radius=12)
        pygame.draw.rect(screen, (50, 62, 90), deck_rect, 1, border_radius=12)

        # Header tag
        tag_rect = pygame.Rect(deck_rect.x + 16, deck_rect.y + 14, 140, 22)
        pygame.draw.rect(screen, (30, 42, 65), tag_rect, border_radius=6)
        self._draw_text_centered(screen, "TURNO DE COMBATE", tag_rect, self._get_font("tiny"), UI_ACCENT)

        # Main question
        med_bold = self._get_font("medium_bold", "medium")
        self._draw_text_with_shadow(screen, "O que vai fazer?", (deck_rect.x + 16, deck_rect.y + 40),
                                    med_bold, WHITE)

        # Dynamic tip based on hovered/selected action
        sel_meta = self.ACTIONS[selected % len(self.ACTIONS)]
        tip_box = pygame.Rect(deck_rect.x + 16, deck_rect.y + 72, deck_rect.width - 32, 70)
        pygame.draw.rect(screen, (16, 18, 28), tip_box, border_radius=8)
        pygame.draw.rect(screen, sel_meta["color"], tip_box, 1, border_radius=8)

        # Action tip title + info
        small_bold = self._get_font("small_bold", "small")
        small_font = self._get_font("small")
        self._draw_action_icon(screen, sel_meta["icon_type"], tip_box.x + 8, tip_box.y + 7, 16, sel_meta["color"])
        self._draw_text_with_shadow(screen, sel_meta["title"],
                                    (tip_box.x + 30, tip_box.y + 6), small_bold, sel_meta["color"])

        action_tips = {
            "attack": "Golpes matemáticos causam dano ampliado com acertos rápidos!",
            "defend": "Postura defensiva reduz pela metade o dano do ataque inimigo!",
            "item": "Abre a mochila de combate para usar itens e poções de cura.",
            "run": "Tenta escapar com segurança desta batalha contra MathMon selvagem.",
        }
        tip_text = action_tips.get(sel_meta["id"], "")
        wrapped_tip = wrap_text(tip_text, small_font, tip_box.width - 20)
        for line_i, line_str in enumerate(wrapped_tip[:2]):
            self._draw_text_with_shadow(screen, line_str, (tip_box.x + 10, tip_box.y + 28 + line_i * 18),
                                        self._get_font("tiny"), (185, 195, 215))

        # Controls hint at bottom
        hint_str = "Setas / WASD / Mouse para navegar"
        self._draw_text_with_shadow(screen, hint_str, (deck_rect.x + 16, deck_rect.y + 154),
                                    self._get_font("tiny"), (130, 140, 165))

        # ─── Right Action Buttons (2x2 Grid) ───
        btn_width = 206
        btn_height = 86
        col0_x = 352
        col1_x = 570
        row0_y = menu_y + 16
        row1_y = menu_y + 116

        self._action_rects = []
        for i, act in enumerate(self.ACTIONS):
            bx = col0_x if (i % 2 == 0) else col1_x
            by = row0_y if (i < 2) else row1_y
            btn_rect = pygame.Rect(bx, by, btn_width, btn_height)
            self._action_rects.append(btn_rect)

            is_sel = (i == selected)
            theme_col = act["color"]

            if is_sel:
                # Active Glowing Card
                glow_surf = pygame.Surface((btn_width + 10, btn_height + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*theme_col, 50), (0, 0, btn_width + 10, btn_height + 10), border_radius=14)
                screen.blit(glow_surf, (bx - 5, by - 5))

                pygame.draw.rect(screen, (28, 34, 52), btn_rect, border_radius=12)
                pygame.draw.rect(screen, theme_col, btn_rect, 3, border_radius=12)

                # Left highlight strip
                pygame.draw.rect(screen, theme_col, (bx, by + 4, 8, btn_height - 8), border_radius=4)

                # Selector arrow indicator
                self._draw_polygon_arrow(screen, bx + 16, by + btn_height // 2, 6, theme_col, "right")

                # Action icon and title
                icon_x = bx + 28
                self._draw_action_icon(screen, act["icon_type"], icon_x, by + 18, 20, theme_col)
                self._draw_text_with_shadow(screen, act["title"],
                                            (icon_x + 26, by + 16), med_bold, WHITE, BLACK)
                self._draw_text_with_shadow(screen, act["subtitle"],
                                            (icon_x + 4, by + 48), small_font, theme_col, BLACK)
            else:
                # Sleek Inactive Card
                pygame.draw.rect(screen, (22, 26, 40), btn_rect, border_radius=12)
                pygame.draw.rect(screen, (50, 60, 85), btn_rect, 1, border_radius=12)

                # Left color accent notch
                pygame.draw.rect(screen, theme_col, (bx, by + 8, 5, btn_height - 16), border_radius=3)

                # Action icon and title
                icon_x = bx + 18
                self._draw_action_icon(screen, act["icon_type"], icon_x, by + 20, 20, (180, 190, 210))
                self._draw_text_with_shadow(screen, act["title"],
                                            (icon_x + 26, by + 18), med_bold, (230, 235, 245), BLACK)
                self._draw_text_with_shadow(screen, act["subtitle"],
                                            (icon_x + 4, by + 48), small_font, (155, 165, 185), BLACK)

    # ─── MOVE SELECTION MENU (FIXING WHITE-ON-WHITE LETTERS) ────────

    def draw_move_menu(self, screen, moves, selected):
        """Draw the move cards and dedicated strategy preview card."""
        menu_y = BATTLE_PANEL_Y
        self._draw_panel_background(screen, menu_y)

        # 4 Move cards on the Left (2x2 grid)
        btn_width = 244
        btn_height = 86
        col0_x = 24
        col1_x = 278
        row0_y = menu_y + 16
        row1_y = menu_y + 116

        self._move_rects = []
        for i, move in enumerate(moves):
            bx = col0_x if (i % 2 == 0) else col1_x
            by = row0_y if (i < 2) else row1_y
            btn_rect = pygame.Rect(bx, by, btn_width, btn_height)
            self._move_rects.append(btn_rect)

            is_sel = (i == selected)
            m_type = move.get("type", "normal")
            type_color = self.TYPE_COLORS.get(m_type, (160, 170, 190))
            ch_type = move.get("challenge_type", CHALLENGE_MATH)
            ch_meta = self.CHALLENGE_META.get(ch_type, self.CHALLENGE_META[CHALLENGE_MATH])

            if is_sel:
                # Outer glow
                glow_surf = pygame.Surface((btn_width + 8, btn_height + 8), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*type_color, 45), (0, 0, btn_width + 8, btn_height + 8), border_radius=14)
                screen.blit(glow_surf, (bx - 4, by - 4))

                # Active card body
                pygame.draw.rect(screen, (30, 36, 56), btn_rect, border_radius=12)
                pygame.draw.rect(screen, type_color, btn_rect, 3, border_radius=12)

                # Selector arrow
                self._draw_polygon_arrow(screen, bx + 12, by + btn_height // 2, 5, type_color, "right")
                text_start_x = bx + 24
            else:
                # Inactive card body - high contrast, rich slate
                pygame.draw.rect(screen, (22, 26, 40), btn_rect, border_radius=12)
                pygame.draw.rect(screen, (50, 60, 85), btn_rect, 1, border_radius=12)
                # Left type accent bar
                pygame.draw.rect(screen, type_color, (bx, by + 6, 5, btn_height - 12), border_radius=3)
                text_start_x = bx + 14

            # Move Name: ALWAYS CRISP AND FULLY OPAQUE
            med_bold = self._get_font("medium_bold", "medium")
            title_color = WHITE if is_sel else (235, 240, 250)
            self._draw_text_with_shadow(screen, move["name"], (text_start_x, by + 12), med_bold, title_color, BLACK)

            # Move Type Pill (dynamic width so no names are truncated)
            type_str = m_type.upper()
            tiny_font = self._get_font("tiny")
            t_w = tiny_font.size(type_str)[0] + 14
            type_tag_rect = pygame.Rect(text_start_x, by + 46, t_w, 20)
            pygame.draw.rect(screen, type_color, type_tag_rect, border_radius=4)
            self._draw_text_centered(screen, type_str, type_tag_rect, tiny_font, WHITE, BLACK)

            # Challenge Type Pill
            ch_str = ch_meta["short"]
            c_w = tiny_font.size(ch_str)[0] + 14
            ch_tag_rect = pygame.Rect(text_start_x + t_w + 6, by + 46, c_w, 20)
            pygame.draw.rect(screen, ch_meta["tag_bg"], ch_tag_rect, border_radius=4)
            pygame.draw.rect(screen, ch_meta["color"], ch_tag_rect, 1, border_radius=4)
            self._draw_text_centered(screen, ch_str, ch_tag_rect, tiny_font, ch_meta["color"], BLACK)

            # Power display
            p_val = move.get("power", 0)
            p_str = f"Poder: {p_val}"
            small_font = self._get_font("small")
            p_col = UI_HIGHLIGHT if is_sel else (175, 185, 205)
            self._draw_text_with_shadow(screen, p_str, (bx + btn_width - 78, by + 46), small_font, p_col, BLACK)

        # ─── Right Dedicated Move Detail Card ───
        detail_rect = pygame.Rect(534, menu_y + 16, 242, 186)
        pygame.draw.rect(screen, (22, 26, 40), detail_rect, border_radius=12)
        pygame.draw.rect(screen, (55, 68, 95), detail_rect, 1, border_radius=12)

        if 0 <= selected < len(moves):
            curr_move = moves[selected]
            curr_type = curr_move.get("type", "normal")
            c_color = self.TYPE_COLORS.get(curr_type, UI_ACCENT)
            c_meta = self.CHALLENGE_META.get(curr_move.get("challenge_type"), self.CHALLENGE_META[CHALLENGE_MATH])

            # Header bar
            pygame.draw.rect(screen, (30, 38, 58), (detail_rect.x, detail_rect.y, detail_rect.width, 36),
                             border_top_left_radius=12, border_top_right_radius=12)
            pygame.draw.rect(screen, c_color, (detail_rect.x + 12, detail_rect.y + 34, detail_rect.width - 24, 2))

            self._draw_text_with_shadow(screen, curr_move["name"], (detail_rect.x + 12, detail_rect.y + 7),
                                        self._get_font("medium_bold", "medium"), WHITE, BLACK)

            # Challenge info banner
            ch_box = pygame.Rect(detail_rect.x + 10, detail_rect.y + 44, detail_rect.width - 20, 24)
            pygame.draw.rect(screen, c_meta["tag_bg"], ch_box, border_radius=6)
            pygame.draw.rect(screen, c_meta["color"], ch_box, 1, border_radius=6)
            self._draw_text_centered(screen, f"Desafio: {c_meta['label']}",
                                     ch_box, self._get_font("tiny"), c_meta["color"], BLACK)

            # Description (word-wrapped)
            desc_text = curr_move.get("description", c_meta["desc"])
            wrapped = wrap_text(desc_text, self._get_font("small"), detail_rect.width - 24)
            for li, line in enumerate(wrapped[:3]):
                self._draw_text_with_shadow(screen, line, (detail_rect.x + 12, detail_rect.y + 76 + li * 16),
                                            self._get_font("small"), (200, 210, 225), BLACK)

        # Bottom return button (ESC)
        self._back_rect = pygame.Rect(detail_rect.x + 12, detail_rect.bottom - 36, detail_rect.width - 24, 26)
        pygame.draw.rect(screen, (32, 38, 56), self._back_rect, border_radius=6)
        pygame.draw.rect(screen, (75, 85, 115), self._back_rect, 1, border_radius=6)
        self._draw_text_centered(screen, "◄ ESC / X : Voltar", self._back_rect, self._get_font("small"), (240, 245, 255), BLACK)

    # ─── CHALLENGE SCREEN (MATH / EQUATION / MULTIPLE CHOICE) ───────

    def draw_challenge_screen(self, screen, challenge, answer_text, time_remaining, selected_option=None):
        """Draw the high-tech math battle question screen."""
        menu_y = BATTLE_CHALLENGE_Y
        menu_height = SCREEN_HEIGHT - menu_y

        # Completely OPAQUE base to eliminate any ghosting from prior frames
        pygame.draw.rect(screen, (16, 20, 32), (0, menu_y, SCREEN_WIDTH, menu_height))
        pygame.draw.line(screen, UI_ACCENT, (0, menu_y), (SCREEN_WIDTH, menu_y), 2)

        # ─── Top Timer Bar ───
        max_timer = challenge.get("timer", 15)
        timer_ratio = max(0.0, min(1.0, time_remaining / max_timer)) if max_timer > 0 else 0.0

        bar_x = 40
        bar_y = menu_y + 12
        bar_w = SCREEN_WIDTH - 80
        bar_h = 10

        pygame.draw.rect(screen, (12, 14, 20), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        pygame.draw.rect(screen, (55, 68, 90), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)

        if timer_ratio > 0.5:
            t_col = HP_GREEN
        elif timer_ratio > 0.25:
            t_col = HP_YELLOW
        else:
            t_col = HP_RED

        fill_timer_w = int(bar_w * timer_ratio)
        if fill_timer_w > 0:
            if timer_ratio <= 0.25 and int(time.time() * 8) % 2:
                t_col = (255, 140, 140)
            pygame.draw.rect(screen, t_col, (bar_x + 1, bar_y + 1, fill_timer_w - 2, bar_h - 2), border_radius=3)

        # Timer countdown text
        timer_str = f"TEMPO: {time_remaining:.1f}s"
        small_bold = self._get_font("small_bold", "small")
        self._draw_text_with_shadow(screen, timer_str, (bar_x + bar_w - 95, bar_y - 12), small_bold, t_col, BLACK)

        # ─── Question Box ───
        q_box = pygame.Rect(80, menu_y + 36, SCREEN_WIDTH - 160, 66)
        pygame.draw.rect(screen, (22, 28, 44), q_box, border_radius=12)
        pygame.draw.rect(screen, (65, 82, 118), q_box, 2, border_radius=12)

        q_text = challenge.get("question", "")
        large_font = self._get_font("large")
        self._draw_text_centered(screen, q_text, q_box, large_font, UI_HIGHLIGHT, BLACK)

        # ─── Answer Options / Input Mode ───
        options = challenge.get("options", [])
        self._option_rects = []

        if options:
            # Multiple-Choice Cards
            n_opts = len(options)
            opt_h = 50
            opt_y = menu_y + 118
            total_gap = (n_opts - 1) * 16
            avail_w = SCREEN_WIDTH - 120
            opt_w = (avail_w - total_gap) // n_opts
            start_x = 60

            for i, opt in enumerate(options):
                ox = start_x + i * (opt_w + 16)
                o_rect = pygame.Rect(ox, opt_y, opt_w, opt_h)
                self._option_rects.append(o_rect)

                is_sel = (selected_option is not None and i == selected_option)

                if is_sel:
                    # Glowing Selected Card
                    glow_surf = pygame.Surface((opt_w + 6, opt_h + 6), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, (*UI_HIGHLIGHT, 60), (0, 0, opt_w + 6, opt_h + 6), border_radius=12)
                    screen.blit(glow_surf, (ox - 3, opt_y - 3))

                    pygame.draw.rect(screen, UI_HIGHLIGHT, o_rect, border_radius=10)
                    pygame.draw.rect(screen, WHITE, o_rect, 2, border_radius=10)

                    # Top indicator
                    self._draw_polygon_arrow(screen, ox + opt_w // 2, opt_y - 4, 5, UI_HIGHLIGHT, "down")

                    # High contrast dark text on gold
                    self._draw_text_centered(screen, str(opt), o_rect, large_font, (18, 20, 28), None)
                else:
                    pygame.draw.rect(screen, (26, 32, 50), o_rect, border_radius=10)
                    pygame.draw.rect(screen, (60, 75, 105), o_rect, 1, border_radius=10)
                    self._draw_text_centered(screen, str(opt), o_rect, large_font, (240, 245, 255), BLACK)

                # Keycap indicator [1], [2], [3]
                key_rect = pygame.Rect(ox + 8, opt_y + 6, 20, 18)
                pygame.draw.rect(screen, (15, 18, 26), key_rect, border_radius=4)
                self._draw_text_centered(screen, str(i + 1), key_rect, self._get_font("tiny"),
                                         WHITE if is_sel else (140, 150, 175), None)

            # Footer hint
            hint_str = "Use as TECLAS [1-4], SETAS ou CLIQUE para escolher"
            self._draw_text_centered(screen, hint_str, pygame.Rect(0, menu_y + 192, SCREEN_WIDTH, 20),
                                     self._get_font("small"), (150, 160, 185))
        else:
            # Direct Keyboard Input Box
            in_w = 260
            in_h = 52
            in_x = SCREEN_WIDTH // 2 - in_w // 2
            in_y = menu_y + 116
            in_rect = pygame.Rect(in_x, in_y, in_w, in_h)

            pygame.draw.rect(screen, (12, 16, 26), in_rect, border_radius=10)
            pygame.draw.rect(screen, UI_ACCENT, in_rect, 2, border_radius=10)

            # Answer text
            ans_font = self._get_font("large")
            if answer_text:
                self._draw_text_centered(screen, answer_text, in_rect, ans_font, WHITE, BLACK)

            # Blinking cursor
            if int(time.time() * 3) % 2:
                tw = ans_font.size(answer_text)[0] if answer_text else 0
                cx = in_rect.centerx + tw // 2 + 3
                pygame.draw.line(screen, UI_ACCENT, (cx, in_y + 10), (cx, in_y + in_h - 10), 2)

            hint_str = "Digite o valor numérico e pressione ENTER"
            self._draw_text_centered(screen, hint_str, pygame.Rect(0, menu_y + 190, SCREEN_WIDTH, 20),
                                     self._get_font("small"), (150, 160, 185))

    # ─── MEMORY CHALLENGE ───────────────────────────────────────────

    def draw_memory_challenge(self, screen, challenge, phase, show_index, player_input, time_remaining):
        """Draw memory challenge with glowing gems and sequence slots."""
        menu_y = BATTLE_CHALLENGE_Y - 10
        menu_height = SCREEN_HEIGHT - menu_y

        pygame.draw.rect(screen, (16, 20, 32), (0, menu_y, SCREEN_WIDTH, menu_height))
        pygame.draw.line(screen, UI_ACCENT, (0, menu_y), (SCREEN_WIDTH, menu_y), 2)

        sequence = challenge.get("sequence", [])
        ch_type = challenge.get("type", "memory_numbers")

        if phase == "show":
            title_rect = pygame.Rect(0, menu_y + 14, SCREEN_WIDTH, 30)
            self._draw_text_centered(screen, "MEMORIZE A SEQUÊNCIA!", title_rect,
                                     self._get_font("medium_bold", "medium"), UI_HIGHLIGHT)

            elem_size = 56
            gap = 14
            total_w = len(sequence) * (elem_size + gap) - gap
            start_x = SCREEN_WIDTH // 2 - total_w // 2

            for i, elem in enumerate(sequence):
                ex = start_x + i * (elem_size + gap)
                ey = menu_y + 65
                card_rect = pygame.Rect(ex, ey, elem_size, elem_size)

                if i <= show_index:
                    is_current = (i == show_index)
                    if ch_type == "memory_numbers":
                        col = UI_HIGHLIGHT if is_current else UI_ACCENT
                        pygame.draw.rect(screen, col, card_rect, border_radius=10)
                        pygame.draw.rect(screen, WHITE, card_rect, 2 if is_current else 1, border_radius=10)
                        self._draw_text_centered(screen, str(elem), card_rect, self._get_font("large"),
                                                 (16, 20, 30), None)
                    else:
                        col = self.memory_colors_map.get(elem, (200, 200, 200))
                        pygame.draw.rect(screen, col, card_rect, border_radius=10)
                        if is_current:
                            pygame.draw.rect(screen, WHITE, card_rect, 3, border_radius=10)
                else:
                    pygame.draw.rect(screen, (32, 38, 56), card_rect, border_radius=10)
                    pygame.draw.rect(screen, (55, 65, 88), card_rect, 1, border_radius=10)
                    self._draw_text_centered(screen, "?", card_rect, self._get_font("large"), (80, 95, 125))

        elif phase == "input":
            input_timer = challenge.get("input_timer", 10)
            t_ratio = max(0.0, min(1.0, time_remaining / input_timer))
            t_col = HP_GREEN if t_ratio > 0.5 else HP_RED

            pygame.draw.rect(screen, (12, 14, 20), (40, menu_y + 12, SCREEN_WIDTH - 80, 8), border_radius=4)
            fill_w = int((SCREEN_WIDTH - 80) * t_ratio)
            if fill_w > 0:
                pygame.draw.rect(screen, t_col, (40, menu_y + 12, fill_w, 8), border_radius=4)

            title_rect = pygame.Rect(0, menu_y + 26, SCREEN_WIDTH, 26)
            self._draw_text_centered(screen, "REPITA A SEQUÊNCIA!", title_rect,
                                     self._get_font("medium_bold", "medium"), UI_HIGHLIGHT)

            if ch_type == "memory_numbers":
                elem_size = 54
                gap = 14
                total_w = len(sequence) * (elem_size + gap) - gap
                start_x = SCREEN_WIDTH // 2 - total_w // 2

                for i in range(len(sequence)):
                    ex = start_x + i * (elem_size + gap)
                    ey = menu_y + 64
                    card_rect = pygame.Rect(ex, ey, elem_size, elem_size)

                    if i < len(player_input):
                        pygame.draw.rect(screen, UI_ACCENT, card_rect, border_radius=10)
                        self._draw_text_centered(screen, str(player_input[i]), card_rect,
                                                 self._get_font("large"), (16, 20, 30), None)
                    else:
                        pygame.draw.rect(screen, (30, 36, 54), card_rect, border_radius=10)
                        b_col = UI_HIGHLIGHT if i == len(player_input) else (55, 65, 88)
                        pygame.draw.rect(screen, b_col, card_rect, 2 if i == len(player_input) else 1, border_radius=10)

                hint_rect = pygame.Rect(0, menu_y + 140, SCREEN_WIDTH, 20)
                self._draw_text_centered(screen, "Digite os números no teclado (1 a 9)", hint_rect,
                                         self._get_font("small"), (160, 175, 200))
            else:
                color_options = list(self.memory_colors_map.keys())
                color_names = challenge.get("color_names", {})
                btn_w = 88
                total_w = len(color_options) * (btn_w + 10) - 10
                start_x = SCREEN_WIDTH // 2 - total_w // 2

                for i, cc in enumerate(color_options):
                    bx = start_x + i * (btn_w + 10)
                    by = menu_y + 68
                    col_rect = pygame.Rect(bx, by, btn_w, 44)
                    col = self.memory_colors_map[cc]
                    pygame.draw.rect(screen, col, col_rect, border_radius=8)
                    pygame.draw.rect(screen, WHITE, col_rect, 1, border_radius=8)

                    lbl = color_names.get(cc, cc)
                    self._draw_text_centered(screen, lbl, col_rect, self._get_font("small_bold", "small"), WHITE, BLACK)

                    # Keycap hint
                    k_rect = pygame.Rect(bx + btn_w // 2 - 10, by + 50, 20, 18)
                    pygame.draw.rect(screen, (24, 30, 45), k_rect, border_radius=4)
                    self._draw_text_centered(screen, str(i + 1), k_rect, self._get_font("tiny"), WHITE)

                prog_str = f"Progresso: {len(player_input)} / {len(sequence)}"
                self._draw_text_centered(screen, prog_str, pygame.Rect(0, menu_y + 152, SCREEN_WIDTH, 20),
                                         self._get_font("small"), UI_ACCENT)

    # ─── ITEM SELECTION MENU ────────────────────────────────────────

    def draw_item_menu(self, screen, inventory, selected):
        """Draw a modern 2-column item bag with preview details."""
        menu_y = BATTLE_PANEL_Y
        self._draw_panel_background(screen, menu_y)

        # Left Column: Usable Item Cards List
        list_rect = pygame.Rect(24, menu_y + 16, 470, 188)
        pygame.draw.rect(screen, (22, 26, 40), list_rect, border_radius=12)
        pygame.draw.rect(screen, (55, 68, 95), list_rect, 1, border_radius=12)

        # Header
        pygame.draw.rect(screen, (30, 38, 58), (list_rect.x, list_rect.y, list_rect.width, 32),
                         border_top_left_radius=12, border_top_right_radius=12)
        self._draw_text_with_shadow(screen, "ITENS DISPONÍVEIS NA MOCHILA", (list_rect.x + 14, list_rect.y + 7),
                                    self._get_font("small_bold", "small"), UI_HIGHLIGHT)

        items = list(BATTLE_ITEMS)
        self._item_rects = []
        for i, item_id in enumerate(items):
            item = ITEMS_DB.get(item_id, {"name": item_id, "description": ""})
            qty = inventory.get(item_id, 0)
            iy = list_rect.y + 40 + i * 44
            row_rect = pygame.Rect(list_rect.x + 8, iy, list_rect.width - 16, 38)
            self._item_rects.append(row_rect)

            is_sel = (i == selected)

            if is_sel:
                pygame.draw.rect(screen, (34, 44, 70), row_rect, border_radius=8)
                pygame.draw.rect(screen, UI_HIGHLIGHT, row_rect, 2, border_radius=8)
                self._draw_polygon_arrow(screen, row_rect.x + 10, row_rect.centery, 5, UI_HIGHLIGHT, "right")
                tx = row_rect.x + 24
            else:
                pygame.draw.rect(screen, (26, 30, 46), row_rect, border_radius=8)
                pygame.draw.rect(screen, (45, 55, 78), row_rect, 1, border_radius=8)
                tx = row_rect.x + 14

            # Item Name
            name_col = WHITE if (qty > 0) else (140, 145, 160)
            med_bold = self._get_font("medium_bold", "medium")
            # Vertically centered text
            self._draw_text_with_shadow(screen, item["name"], (tx, iy + (row_rect.height - med_bold.get_height()) // 2),
                                        med_bold, name_col, BLACK)

            # Quantity pill
            qty_str = f"x{qty}"
            q_col = UI_HIGHLIGHT if (qty > 0) else (160, 80, 80)
            qty_rect = pygame.Rect(row_rect.right - 55, iy + 8, 45, 22)
            pygame.draw.rect(screen, (16, 20, 30), qty_rect, border_radius=6)
            self._draw_text_centered(screen, qty_str, qty_rect, self._get_font("small_bold", "small"), q_col)

        # Right Column: Selected Item Detail Card
        preview_rect = pygame.Rect(508, menu_y + 16, 268, 188)
        pygame.draw.rect(screen, (22, 26, 40), preview_rect, border_radius=12)
        pygame.draw.rect(screen, (55, 68, 95), preview_rect, 1, border_radius=12)

        if 0 <= selected < len(items):
            sel_item_id = items[selected]
            sel_item = ITEMS_DB.get(sel_item_id, {"name": sel_item_id, "description": ""})
            sel_qty = inventory.get(sel_item_id, 0)

            # Header
            pygame.draw.rect(screen, (30, 38, 58), (preview_rect.x, preview_rect.y, preview_rect.width, 36),
                             border_top_left_radius=12, border_top_right_radius=12)
            self._draw_text_with_shadow(screen, sel_item["name"], (preview_rect.x + 14, preview_rect.y + 8),
                                        self._get_font("medium_bold", "medium"), WHITE, BLACK)

            # Description wrapped
            desc_lines = wrap_text(sel_item.get("description", ""), self._get_font("small"), preview_rect.width - 28)
            for li, line in enumerate(desc_lines[:3]):
                self._draw_text_with_shadow(screen, line, (preview_rect.x + 14, preview_rect.y + 48 + li * 18),
                                            self._get_font("small"), (195, 205, 225), BLACK)

            # Status pill
            stat_rect = pygame.Rect(preview_rect.x + 14, preview_rect.y + 110, preview_rect.width - 28, 26)
            if sel_qty > 0:
                pygame.draw.rect(screen, (20, 60, 40), stat_rect, border_radius=6)
                self._draw_text_centered(screen, "Disponível para uso", stat_rect, self._get_font("small"), HP_GREEN)
            else:
                pygame.draw.rect(screen, (60, 25, 25), stat_rect, border_radius=6)
                self._draw_text_centered(screen, "Item esgotado", stat_rect, self._get_font("small"), HP_RED)

        # Back button
        self._back_rect = pygame.Rect(preview_rect.x + 14, preview_rect.bottom - 36, preview_rect.width - 28, 26)
        pygame.draw.rect(screen, (32, 38, 56), self._back_rect, border_radius=6)
        pygame.draw.rect(screen, (75, 85, 115), self._back_rect, 1, border_radius=6)
        self._draw_text_centered(screen, "◄ ESC / X : Voltar", self._back_rect, self._get_font("small"), (240, 245, 255), BLACK)

    # ─── MESSAGE BOX (INTRO / COMBAT LOG) ───────────────────────────

    def draw_message_box(self, screen, messages):
        """Draw dialogue / combat message panel with typing indicator."""
        menu_y = BATTLE_PANEL_Y
        self._draw_panel_background(screen, menu_y)

        # Outer message frame
        box_rect = pygame.Rect(24, menu_y + 16, SCREEN_WIDTH - 48, 188)
        pygame.draw.rect(screen, (22, 26, 40), box_rect, border_radius=12)
        pygame.draw.rect(screen, (55, 68, 95), box_rect, 1, border_radius=12)

        # Tag banner
        tag_rect = pygame.Rect(box_rect.x + 16, box_rect.y + 14, 96, 22)
        pygame.draw.rect(screen, (32, 42, 68), tag_rect, border_radius=6)
        self._draw_text_centered(screen, "BATALHA", tag_rect, self._get_font("tiny"), UI_ACCENT)

        if not messages:
            hint = "Pressione ENTER ou Z para prosseguir..."
            self._draw_text_with_shadow(screen, hint, (box_rect.x + 16, box_rect.y + 54),
                                        self._get_font("medium"), (170, 180, 205), BLACK)
            return

        msg = messages[0]
        # Multi-line wrap support
        med_font = self._get_font("medium_bold", "medium")
        lines = wrap_text(msg, med_font, box_rect.width - 40)
        for i, line in enumerate(lines[:3]):
            self._draw_text_with_shadow(screen, line, (box_rect.x + 18, box_rect.y + 50 + i * 26),
                                        med_font, WHITE, BLACK)

        # Bouncing prompt indicator
        if int(time.time() * 3) % 2:
            bounce = int(math.sin(time.time() * 8) * 3)
            self._draw_polygon_arrow(screen, box_rect.right - 28, box_rect.bottom - 24 + bounce,
                                     7, UI_HIGHLIGHT, "down")

    # ─── OVERLAYS (RESULT / VICTORY / DEFEAT) ───────────────────────

    def draw_result_overlay(self, screen, correct, message=""):
        """Draw result flash banner."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        col = (35, 190, 85, 45) if correct else (220, 50, 50, 45)
        overlay.fill(col)
        screen.blit(overlay, (0, 0))

        if message:
            banner_w = 420
            banner_h = 70
            bx = SCREEN_WIDTH // 2 - banner_w // 2
            by = SCREEN_HEIGHT // 2 - banner_h // 2
            b_rect = pygame.Rect(bx, by, banner_w, banner_h)

            card_col = (20, 60, 35) if correct else (65, 20, 20)
            edge_col = HP_GREEN if correct else HP_RED
            pygame.draw.rect(screen, card_col, b_rect, border_radius=14)
            pygame.draw.rect(screen, edge_col, b_rect, 3, border_radius=14)

            title_font = self._get_font("title")
            self._draw_text_centered(screen, message, b_rect, title_font, WHITE, BLACK)

    def draw_victory_screen(self, screen, xp_gained, leveled_up, monster):
        """Draw an epic victory celebration overlay."""
        # Clean bottom panel
        self._draw_panel_background(screen)

        # Dim background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 215))
        screen.blit(overlay, (0, 0))

        card_w = 540
        card_h = 280
        cx = SCREEN_WIDTH // 2 - card_w // 2
        cy = 130
        c_rect = pygame.Rect(cx, cy, card_w, card_h)

        pygame.draw.rect(screen, (22, 28, 44), c_rect, border_radius=16)
        pygame.draw.rect(screen, UI_HIGHLIGHT, c_rect, 3, border_radius=16)

        # Header ribbon
        head_rect = pygame.Rect(cx, cy, card_w, 64)
        pygame.draw.rect(screen, (34, 44, 70), head_rect, border_top_left_radius=16, border_top_right_radius=16)
        title_font = self._get_font("huge", "title")
        self._draw_text_centered(screen, "VITÓRIA!", head_rect, title_font, UI_HIGHLIGHT, BLACK)

        # XP gained
        xp_rect = pygame.Rect(cx + 30, cy + 86, card_w - 60, 50)
        pygame.draw.rect(screen, (16, 22, 36), xp_rect, border_radius=10)
        pygame.draw.rect(screen, XP_BLUE, xp_rect, 1, border_radius=10)
        large_font = self._get_font("large")
        self._draw_text_centered(screen, f"+{xp_gained} PONTOS DE EXPERIÊNCIA", xp_rect,
                                 large_font, (100, 215, 255), BLACK)

        # Level up notification
        if leveled_up:
            lvl_rect = pygame.Rect(cx + 30, cy + 150, card_w - 60, 48)
            pygame.draw.rect(screen, (20, 60, 35), lvl_rect, border_radius=10)
            pygame.draw.rect(screen, HP_GREEN, lvl_rect, 2, border_radius=10)
            lvl_str = f"{monster.name} subiu para o NÍVEL {monster.level}!"
            self._draw_text_centered(screen, lvl_str, lvl_rect, large_font, WHITE, BLACK)

        # Prompt hint
        hint_rect = pygame.Rect(cx, cy + 225, card_w, 30)
        if int(time.time() * 2) % 2:
            self._draw_text_centered(screen, "[ Pressione ENTER ou Z para continuar ]",
                                     hint_rect, self._get_font("medium"), (210, 220, 240))

    def draw_defeat_screen(self, screen):
        """Draw defeat screen with comforting feedback."""
        # Clean bottom panel
        self._draw_panel_background(screen)

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((15, 10, 15, 225))
        screen.blit(overlay, (0, 0))

        card_w = 500
        card_h = 240
        cx = SCREEN_WIDTH // 2 - card_w // 2
        cy = 160
        c_rect = pygame.Rect(cx, cy, card_w, card_h)

        pygame.draw.rect(screen, (32, 18, 24), c_rect, border_radius=16)
        pygame.draw.rect(screen, HP_RED, c_rect, 2, border_radius=16)

        head_rect = pygame.Rect(cx, cy, card_w, 60)
        pygame.draw.rect(screen, (48, 22, 30), head_rect, border_top_left_radius=16, border_top_right_radius=16)
        self._draw_text_centered(screen, "DERROTA...", head_rect, self._get_font("huge", "title"), HP_RED, BLACK)

        msg1 = "Seus MathMons foram derrotados e precisam de descanso."
        msg2 = "Eles foram restaurados e recuperaram todas as energias!"
        self._draw_text_centered(screen, msg1, pygame.Rect(cx, cy + 85, card_w, 24),
                                 self._get_font("small"), (220, 200, 205))
        self._draw_text_centered(screen, msg2, pygame.Rect(cx, cy + 115, card_w, 24),
                                 self._get_font("small"), (180, 230, 195))

        hint_rect = pygame.Rect(cx, cy + 180, card_w, 30)
        if int(time.time() * 2) % 2:
            self._draw_text_centered(screen, "[ Pressione ENTER ou Z para voltar ]",
                                     hint_rect, self._get_font("medium"), WHITE)

    # ─── ANIMATION & PARTICLES HELPERS ──────────────────────────────

    def sync_hp(self, player_mon, enemy_mon):
        """Feed current HP targets so bars tween smoothly."""
        self._target_hp["player"] = float(player_mon.current_hp)
        self._target_hp["enemy"] = float(enemy_mon.current_hp)
        if self._display_hp["player"] is None:
            self._display_hp["player"] = float(player_mon.current_hp)
        if self._display_hp["enemy"] is None:
            self._display_hp["enemy"] = float(enemy_mon.current_hp)

    def update(self, dt):
        """Update animation timers, particle physics and smooth HP tween."""
        self.time += dt

        if self.shake_timer > 0:
            self.shake_timer -= dt
        if self.flash_timer > 0:
            self.flash_timer -= dt
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
        if self.result_timer > 0:
            self.result_timer -= dt

        if self.enemy_slide < 1.0:
            self.enemy_slide = min(1.0, self.enemy_slide + dt / ENEMY_INTRO_SLIDE_TIME)

        # Smooth HP tween
        factor = min(1.0, dt * 8.0)
        for side in ("player", "enemy"):
            target = self._target_hp.get(side)
            display = self._display_hp.get(side)
            if target is not None and display is not None:
                delta = int(round((target - display) * factor))
                if delta == 0 and display != target:
                    delta = 1 if target > display else -1
                new_val = display + delta
                if (delta > 0 and new_val > target) or (delta < 0 and new_val < target):
                    new_val = target
                self._display_hp[side] = new_val

        # Particles
        for p in self.particles[:]:
            p["life"] -= dt
            p["vy"] += p.get("gravity", 90.0) * dt
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            if p["life"] <= 0:
                self.particles.remove(p)

        # Damage popups
        for pop in self.damage_popups[:]:
            pop["life"] -= dt
            pop["y"] -= 36 * dt
            if pop["life"] <= 0:
                self.damage_popups.remove(pop)

    def trigger_shake(self, duration=0.3):
        self.shake_timer = duration

    def trigger_flash(self, duration=0.2):
        self.flash_timer = duration

    def trigger_hit(self, duration=0.25):
        self.hit_flash_timer = duration

    def _burst(self, x, y, color, count=16, speed=180):
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed_ = random.uniform(speed * 0.4, speed)
            self.particles.append({
                "x": x, "y": y,
                "vx": math.cos(angle) * speed_,
                "vy": math.sin(angle) * speed_ - 40,
                "life": random.uniform(0.3, 0.65),
                "gravity": 280.0,
                "color": color,
                "size": random.uniform(2, 4),
            })

    def add_hit_particles(self, x, y):
        self._burst(x, y, (255, 235, 120), count=18, speed=200)
        self._burst(x, y, (255, 110, 60), count=12, speed=130)

    def add_confetti(self):
        colors = [FIRE_COLOR, WATER_COLOR, PLANT_COLOR, ELECTRIC_COLOR,
                  UI_HIGHLIGHT, UI_ACCENT, (255, 255, 255)]
        for _ in range(60):
            self.particles.append({
                "x": random.uniform(0, SCREEN_WIDTH),
                "y": random.uniform(-40, SCREEN_HEIGHT * 0.4),
                "vx": random.uniform(-30, 30),
                "vy": random.uniform(25, 100),
                "life": random.uniform(1.2, 2.8),
                "gravity": 35.0,
                "color": random.choice(colors),
                "size": random.uniform(3, 6),
            })

    def spawn_damage_popup(self, x, y, amount, color=WHITE):
        if amount <= 0:
            return
        self.damage_popups.append({
            "x": x, "y": y,
            "text": f"-{amount}",
            "life": 0.95,
            "color": color,
        })

    def _draw_popups(self, screen):
        """Draw damage popups with black outlines for 100% legibility."""
        pop_font = self._get_font("large", "medium")
        for pop in self.damage_popups:
            alpha = int(255 * min(1.0, pop["life"] / 0.5))
            # Text with shadow
            surf = pop_font.render(pop["text"], True, pop["color"])
            shadow = pop_font.render(pop["text"], True, BLACK)
            surf.set_alpha(alpha)
            shadow.set_alpha(alpha)
            px = int(pop["x"] - surf.get_width() // 2)
            py = int(pop["y"] - 20)
            screen.blit(shadow, (px + 2, py + 2))
            screen.blit(surf, (px, py))

        for p in self.particles:
            alpha = int(255 * min(1.0, p["life"] / 0.3))
            psize = max(1, int(p["size"]))
            surf = pygame.Surface((psize * 2, psize * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*p["color"], alpha), (psize, psize), psize)
            screen.blit(surf, (int(p["x"]) - psize, int(p["y"]) - psize))

    def get_enemy_center(self):
        return self.ENEMY_HIT_POS

    def get_player_center(self):
        return self.PLAYER_HIT_POS

    # ─── MOUSE HIT TESTING HELPERS ──────────────────────────────────

    def get_action_at_pos(self, pos):
        """Returns index of clicked action button, or None."""
        for i, rect in enumerate(self._action_rects):
            if rect.collidepoint(pos):
                return i
        return None

    def get_move_at_pos(self, pos):
        """Returns index of clicked move button, or None."""
        for i, rect in enumerate(self._move_rects):
            if rect.collidepoint(pos):
                return i
        return None

    def get_option_at_pos(self, pos):
        """Returns index of clicked challenge option, or None."""
        for i, rect in enumerate(self._option_rects):
            if rect.collidepoint(pos):
                return i
        return None

    def get_item_at_pos(self, pos):
        """Returns index of clicked item row, or None."""
        for i, rect in enumerate(self._item_rects):
            if rect.collidepoint(pos):
                return i
        return None

    def is_back_button_clicked(self, pos):
        """Checks if the back button was clicked."""
        return self._back_rect is not None and self._back_rect.collidepoint(pos)

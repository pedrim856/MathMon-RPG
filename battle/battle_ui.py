# MathMon RPG - Battle UI
import pygame
import math
import random
import time
from settings import *
from utils.sprite_generator import SpriteGenerator
from data.items_db import ITEMS_DB, BATTLE_ITEMS


class BattleUI:
    """Renders the battle screen with animations, particles and juice."""

    # Anchor points for hit effects / damage popups
    ENEMY_HIT_POS = (585, 130)
    PLAYER_HIT_POS = (175, 265)

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

        # Memory challenge
        self.memory_colors_map = {
            "V": (220, 50, 50),
            "Az": (50, 100, 220),
            "Am": (220, 200, 50),
            "Vd": (50, 180, 80),
            "Lj": (240, 150, 30),
            "Rx": (160, 50, 200),
        }

    # ─── Battle scene background / monsters ─────────────────────────

    def draw_battle_scene(self, screen, player_mon, enemy_mon, bg_type="grass"):
        """Draw the battle background and monsters."""
        if bg_type == "cave":
            color_top = (40, 35, 45)
            color_bottom = (65, 55, 60)
            accent = (112, 82, 132)
        elif bg_type == "arena":
            color_top = (110, 80, 70)
            color_bottom = (150, 110, 90)
            accent = (220, 170, 90)
        else:
            color_top = (75, 120, 200)    # Sky top
            color_bottom = (180, 210, 240)  # Sky horizon
            accent = (120, 190, 125)

        scene_height = 380
        scene = pygame.Surface((SCREEN_WIDTH, scene_height))
        for y in range(scene_height):
            ratio = y / scene_height
            r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
            g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
            b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
            pygame.draw.line(scene, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        if bg_type == "grass":
            pygame.draw.circle(scene, (255, 245, 190), (690, 66), 30)
            pygame.draw.circle(scene, (255, 250, 215), (690, 66), 23)
            for x in range(0, SCREEN_WIDTH, 26):
                sway = int(math.sin(self.time * 2 + x) * 2)
                pygame.draw.line(scene, (110, 170, 125),
                                 (x, 275 + sway), (x + 8, 250 + sway), 2)
        elif bg_type == "cave":
            for x, y, radius in [(90, 82, 42), (240, 48, 24), (720, 110, 52)]:
                pygame.draw.circle(scene, (30, 27, 36), (x, y), radius)
                pygame.draw.circle(scene, accent, (x, y), max(3, radius // 5))
            # Dripping water glints
            for i, base in enumerate([(120, 60), (400, 28), (640, 88)]):
                drop_y = base[1] + int((self.time * 40 + i * 30) % 70)
                if drop_y < 200:
                    pygame.draw.circle(scene, (140, 170, 255),
                                       (base[0], drop_y), 2)
        else:
            pygame.draw.rect(scene, (120, 82, 65), (0, 235, SCREEN_WIDTH, 145))
            for x in range(0, SCREEN_WIDTH, 40):
                pygame.draw.line(scene, (165, 112, 75), (x, 235), (x + 18, 380), 2)
            # Spectator banners
            for bx in range(40, 760, 120):
                it = int((self.time * 30) + bx) % 12
                for flag_i in range(3):
                    pygame.draw.rect(scene, (200, 60, 60),
                                     (bx + flag_i * 8, 30 + it + flag_i * 6, 6, 10))
                    pygame.draw.polygon(scene, (220, 180, 60),
                                        [(bx + flag_i * 8, 30 + it + flag_i * 6),
                                         (bx + flag_i * 8 + 10, 33 + it + flag_i * 6),
                                         (bx + flag_i * 8, 40 + it + flag_i * 6)])

        pygame.draw.line(scene, accent, (0, 238), (SCREEN_WIDTH, 238), 2)
        screen.blit(scene, (0, 0))

        platform = pygame.Surface((SCREEN_WIDTH, scene_height), pygame.SRCALPHA)
        pygame.draw.ellipse(platform, (18, 24, 30, 100), (410, 175, 300, 50))
        pygame.draw.ellipse(platform, (55, 110, 85, 255), (420, 160, 280, 60))
        pygame.draw.ellipse(platform, (100, 175, 115, 255), (425, 165, 270, 50))
        pygame.draw.ellipse(platform, (18, 24, 30, 100), (50, 325, 280, 45))
        pygame.draw.ellipse(platform, (55, 110, 85, 255), (60, 310, 260, 50))
        pygame.draw.ellipse(platform, (100, 175, 115, 255), (65, 315, 250, 40))
        screen.blit(platform, (0, 0))

        # Enemy monster (top right) — slides into place on battle start
        enemy_sprite = self.sprite_gen.get_monster_sprite(enemy_mon.monster_id, 96, enemy_mon.is_shiny)
        slide_off = int((1.0 - min(1.0, self.enemy_slide)) * 280)
        enemy_x = 520 + slide_off
        enemy_y = 80 + int(math.sin(time.time() * 2) * 3)
        if self.shake_timer > 0:
            enemy_x += int(math.sin(self.shake_timer * 30) * 5)
        screen.blit(enemy_sprite, (enemy_x, enemy_y))

        # Hit flash on enemy
        if self.hit_flash_timer > 0:
            flash = pygame.Surface(enemy_sprite.get_size(), pygame.SRCALPHA)
            alpha = int(180 * min(1.0, self.hit_flash_timer * 6))
            flash.fill((255, 255, 255, alpha))
            screen.blit(flash, (enemy_x, enemy_y))

        # Player monster (bottom left)
        player_sprite = self.sprite_gen.get_monster_sprite(player_mon.monster_id, 112, player_mon.is_shiny)
        player_x = 120
        player_y = 210
        screen.blit(player_sprite, (player_x, player_y))

        # Enemy info box (top left)
        self._draw_monster_info(screen, enemy_mon, 20, 20, True)

        # Player info box (bottom right)
        self._draw_monster_info(screen, player_mon, 460, 280, False)

        # Damage popups (above everything in the scene)
        self._draw_popups(screen)

    def _draw_monster_info(self, screen, monster, x, y, is_enemy):
        """Draw monster info box with HP bar."""
        width = 260
        height = 75 if is_enemy else 85

        key = "enemy" if is_enemy else "player"
        display_hp = self._display_hp.get(key)
        if display_hp is None:
            display_hp = monster.current_hp

        # Shadow
        shadow_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 100), (4, 4, width, height), border_radius=10)
        screen.blit(shadow_surf, (x, y))

        # Box background
        box_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(box_surf, (*UI_BG, 240), (0, 0, width, height), border_radius=10)
        pygame.draw.rect(box_surf, UI_BORDER, (0, 0, width, height), 2, border_radius=10)
        screen.blit(box_surf, (x, y))

        # Name and level
        name_text = self.fonts["medium"].render(monster.name, True, UI_TEXT)
        screen.blit(name_text, (x + 10, y + 8))

        level_text = self.fonts["small"].render(f"Nv.{monster.level}", True, UI_HIGHLIGHT)
        screen.blit(level_text, (x + width - 50, y + 10))

        # Type icon
        type_icon = self.sprite_gen.get_type_icon(monster.type, 16)
        screen.blit(type_icon, (x + name_text.get_width() + 14, y + 10))

        # HP bar
        hp_bar_x = x + 10
        hp_bar_y = y + 35
        hp_bar_width = width - 60

        hp_label = self.fonts["small"].render("HP", True, HP_GREEN)
        screen.blit(hp_label, (hp_bar_x, hp_bar_y - 1))

        hp_bar = self.sprite_gen.get_hp_bar(display_hp, monster.max_hp, hp_bar_width, 10)
        screen.blit(hp_bar, (hp_bar_x + 25, hp_bar_y))

        hp_text = self.fonts["small"].render(
            f"{int(round(display_hp))}/{monster.max_hp}", True, UI_TEXT
        )
        screen.blit(hp_text, (hp_bar_x + hp_bar_width + 28, hp_bar_y - 2))

        # XP bar (player only)
        if not is_enemy:
            xp_bar_y = y + 55
            xp_needed = max(1, xp_for_level(monster.level))
            xp_bar = self.sprite_gen.get_xp_bar(monster.xp, xp_needed, hp_bar_width + 25, 6)
            screen.blit(xp_bar, (hp_bar_x, xp_bar_y))
            xp_label = self.fonts["small"].render("XP", True, XP_BLUE)
            screen.blit(xp_label, (hp_bar_x + hp_bar_width + 28, xp_bar_y - 3))

    # ─── Bottom menus ───────────────────────────────────────────────

    def _draw_panel_background(self, screen, menu_y=BATTLE_PANEL_Y):
        """Draw the standard bottom panel background."""
        pygame.draw.rect(screen, UI_BG, (0, menu_y, SCREEN_WIDTH, SCREEN_HEIGHT - menu_y))
        pygame.draw.line(screen, UI_BORDER, (0, menu_y),
                         (SCREEN_WIDTH, menu_y), 2)

    def draw_action_menu(self, screen, selected):
        """Draw the main action menu."""
        actions = ["Atacar", "Defender", "Item", "Fugir"]
        menu_y = BATTLE_PANEL_Y
        self._draw_panel_background(screen, menu_y)

        question = self.fonts["medium"].render("O que fazer?", True, UI_TEXT)
        screen.blit(question, (30, menu_y + 15))

        btn_width = 150
        btn_height = 45
        start_x = SCREEN_WIDTH - btn_width * 2 - 40
        start_y = menu_y + 10

        for i, action in enumerate(actions):
            bx = start_x + (i % 2) * (btn_width + 10)
            by = start_y + (i // 2) * (btn_height + 8)

            if i == selected:
                bg_color = UI_HIGHLIGHT
                text_color = BLACK
            else:
                bg_color = UI_BORDER
                text_color = UI_TEXT

            pygame.draw.rect(screen, bg_color, (bx, by, btn_width, btn_height),
                             border_radius=6)
            pygame.draw.rect(screen, (*WHITE, 50) if i == selected else UI_BORDER,
                             (bx, by, btn_width, btn_height), 2, border_radius=6)

            text = self.fonts["medium"].render(action, True, text_color)
            text_rect = text.get_rect(center=(bx + btn_width // 2, by + btn_height // 2))
            screen.blit(text, text_rect)

    def draw_move_menu(self, screen, moves, selected):
        """Draw the move selection menu."""
        menu_y = BATTLE_PANEL_Y
        self._draw_panel_background(screen, menu_y)

        btn_width = 180
        btn_height = 50
        start_x = 20
        start_y = menu_y + 15

        type_colors = {
            "fogo": FIRE_COLOR,
            "agua": WATER_COLOR,
            "planta": PLANT_COLOR,
            "eletrico": ELECTRIC_COLOR,
            "normal": LIGHT_GRAY,
        }

        ch_labels = {
            CHALLENGE_MATH: "Mat",
            CHALLENGE_EQUATION: "Eq",
            CHALLENGE_MEMORY: "Mem",
            CHALLENGE_LOGIC: "Log",
        }

        for i, move in enumerate(moves):
            bx = start_x + (i % 2) * (btn_width + 10)
            by = start_y + (i // 2) * (btn_height + 10)

            move_type = move.get("type", "normal")
            base_color = type_colors.get(move_type, LIGHT_GRAY)

            if i == selected:
                bg_color = base_color
                border_color = WHITE
                text_color = BLACK
                shadow_offset = 2
            else:
                bg_color = tuple(max(0, c - 60) for c in base_color)
                border_color = base_color
                text_color = UI_TEXT
                shadow_offset = 4

            pygame.draw.rect(screen, (0, 0, 0, 80),
                             (bx, by + shadow_offset, btn_width, btn_height), border_radius=8)
            pygame.draw.rect(screen, bg_color, (bx, by, btn_width, btn_height), border_radius=8)
            pygame.draw.rect(screen, (255, 255, 255, 40),
                             (bx, by, btn_width, btn_height // 2), border_radius=8)
            pygame.draw.rect(screen, border_color,
                             (bx, by, btn_width, btn_height),
                             2 if i == selected else 1, border_radius=8)

            text = self.fonts["small"].render(move["name"], True, text_color)
            screen.blit(text, (bx + 12, by + 8))

            power_text = self.fonts["small"].render(f"Poder: {move['power']}", True, text_color)
            screen.blit(power_text, (bx + 12, by + 28))

            ch_type = move.get("challenge_type", CHALLENGE_MATH)
            badge_surf = pygame.Surface((40, 20), pygame.SRCALPHA)
            pygame.draw.rect(badge_surf, (0, 0, 0, 100), (0, 0, 40, 20), border_radius=4)
            ch_text = self.fonts["small"].render(
                ch_labels.get(ch_type, "?"), True, WHITE if i == selected else text_color
            )
            badge_surf.blit(ch_text, ch_text.get_rect(center=(20, 10)))
            screen.blit(badge_surf, (bx + btn_width - 48, by + 25))

        back_text = self.fonts["small"].render("ESC: Voltar", True, LIGHT_GRAY)
        screen.blit(back_text, (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 25))

        if 0 <= selected < len(moves):
            desc = moves[selected].get("description", "")
            desc_text = self.fonts["small"].render(desc, True, UI_ACCENT)
            screen.blit(desc_text, (start_x + btn_width * 2 + 30, start_y + 20))

    def draw_challenge_screen(self, screen, challenge, answer_text, time_remaining,
                              selected_option=None):
        """Draw the challenge/question screen."""
        menu_y = BATTLE_CHALLENGE_Y
        menu_height = SCREEN_HEIGHT - menu_y

        overlay = pygame.Surface((SCREEN_WIDTH, menu_height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (*UI_BG, 242), (0, 0, SCREEN_WIDTH, menu_height),
                         border_radius=12)
        screen.blit(overlay, (0, menu_y))
        pygame.draw.line(screen, UI_ACCENT, (0, menu_y), (SCREEN_WIDTH, menu_y), 2)

        # Timer bar
        if challenge.get("timer"):
            timer_width = SCREEN_WIDTH - 40
            timer_ratio = max(0, time_remaining / challenge["timer"])
            timer_color = HP_GREEN if timer_ratio > 0.5 \
                else (HP_YELLOW if timer_ratio > 0.25 else HP_RED)

            pygame.draw.rect(screen, DARK_GRAY, (20, menu_y + 8, timer_width, 8),
                             border_radius=4)
            if timer_ratio > 0:
                fill_w = int(timer_width * timer_ratio)
                # Low-timer pulse
                if timer_ratio <= 0.25 and int(time.time() * 6) % 2:
                    fill_w = 0
                pygame.draw.rect(screen, timer_color,
                                 (20, menu_y + 8, fill_w, 8), border_radius=4)

            timer_text = self.fonts["small"].render(f"{time_remaining:.1f}s", True,
                                                     timer_color)
            screen.blit(timer_text, (SCREEN_WIDTH - 60, menu_y + 5))

        # Question text
        q_text = challenge.get("question", "")
        question_surf = self.fonts["large"].render(q_text, True, UI_HIGHLIGHT)
        q_rect = question_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=menu_y + 28)
        screen.blit(question_surf, q_rect)

        ch_type = challenge.get("type", "input")

        if ch_type == "input":
            box_width = 220
            box_height = 50
            box_x = SCREEN_WIDTH // 2 - box_width // 2
            box_y = menu_y + 70

            pygame.draw.rect(screen, (0, 0, 0, 100),
                             (box_x + 2, box_y + 4, box_width, box_height), border_radius=8)
            pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height),
                             border_radius=8)
            pygame.draw.rect(screen, UI_ACCENT, (box_x, box_y, box_width, box_height), 3,
                             border_radius=8)

            ans_surf = self.fonts["large"].render(answer_text, True, BLACK)
            ans_rect = ans_surf.get_rect(
                center=(box_x + box_width // 2, box_y + box_height // 2)
            )
            screen.blit(ans_surf, ans_rect)

            if int(time.time() * 3) % 2:
                cursor_x = ans_rect.right + 2
                pygame.draw.line(screen, BLACK, (cursor_x, box_y + 8),
                                 (cursor_x, box_y + box_height - 8), 2)

            # Selectable multiple-choice options
            options = challenge.get("options", [])
            if options:
                opt_start_x = 60
                opt_y = menu_y + 128
                opt_width = (SCREEN_WIDTH - 120) // len(options)
                opt_height = 36
                for i, opt in enumerate(options):
                    ox = opt_start_x + i * opt_width
                    is_sel = (selected_option is not None and i == selected_option)

                    if is_sel:
                        sel_surf = pygame.Surface((opt_width - 10, opt_height), pygame.SRCALPHA)
                        pygame.draw.rect(sel_surf, (*UI_HIGHLIGHT, 200),
                                         (0, 0, opt_width - 10, opt_height), border_radius=5)
                        screen.blit(sel_surf, (ox, opt_y))
                        pygame.draw.rect(screen, UI_HIGHLIGHT,
                                         (ox, opt_y, opt_width - 10, opt_height), 2,
                                         border_radius=5)
                        arrow = self.fonts["small"].render("▶", True, BLACK)
                        screen.blit(arrow, (ox + 6, opt_y + (opt_height - arrow.get_height()) // 2))
                        opt_color = BLACK
                    else:
                        pygame.draw.rect(screen, UI_BORDER, (ox, opt_y, opt_width - 10, opt_height),
                                         border_radius=5)
                        opt_color = UI_TEXT

                    opt_text = self.fonts["medium"].render(opt, True, opt_color)
                    opt_rect = opt_text.get_rect(
                        center=(ox + (opt_width - 10) // 2, opt_y + opt_height // 2)
                    )
                    screen.blit(opt_text, opt_rect)

                    # Key hint for each option
                    key_hint = self.fonts["small"].render(str(i + 1), True, MID_GRAY)
                    screen.blit(key_hint, (ox + 6, opt_y + opt_height + 4))

                hint = self.fonts["small"].render(
                    "← → selecionar opção, ENTER confirmar, ou digite a resposta", True,
                    LIGHT_GRAY
                )
            else:
                hint = self.fonts["small"].render(
                    "Digite a resposta e pressione ENTER", True, LIGHT_GRAY
                )
            screen.blit(hint, hint.get_rect(centerx=SCREEN_WIDTH // 2, y=menu_y + 185))

    def draw_memory_challenge(self, screen, challenge, phase, show_index, player_input,
                              time_remaining):
        """Draw memory challenge screen."""
        menu_y = BATTLE_CHALLENGE_Y - 20
        menu_height = SCREEN_HEIGHT - menu_y

        overlay = pygame.Surface((SCREEN_WIDTH, menu_height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (*UI_BG, 242), (0, 0, SCREEN_WIDTH, menu_height),
                         border_radius=12)
        screen.blit(overlay, (0, menu_y))
        pygame.draw.line(screen, UI_ACCENT, (0, menu_y), (SCREEN_WIDTH, menu_y), 2)

        sequence = challenge.get("sequence", [])
        ch_type = challenge.get("type", "memory_numbers")

        if phase == "show":
            title = self.fonts["medium"].render("MEMORIZE!", True, UI_HIGHLIGHT)
            screen.blit(title, title.get_rect(centerx=SCREEN_WIDTH // 2, y=menu_y + 10))

            elem_size = 50
            gap = 10
            total_width = len(sequence) * (elem_size + gap) - gap
            start_x = SCREEN_WIDTH // 2 - total_width // 2

            for i, element in enumerate(sequence):
                ex = start_x + i * (elem_size + gap)
                ey = menu_y + 50

                if i <= show_index:
                    if ch_type == "memory_numbers":
                        color = UI_HIGHLIGHT if i == show_index else UI_ACCENT
                        pygame.draw.rect(screen, color, (ex, ey, elem_size, elem_size),
                                         border_radius=8)
                        num_text = self.fonts["large"].render(str(element), True, BLACK)
                        num_rect = num_text.get_rect(center=(ex + elem_size // 2,
                                                              ey + elem_size // 2))
                        screen.blit(num_text, num_rect)
                    else:
                        color = self.memory_colors_map.get(element, (200, 200, 200))
                        pygame.draw.rect(screen, color, (ex, ey, elem_size, elem_size),
                                         border_radius=8)
                        if i == show_index:
                            pygame.draw.rect(screen, WHITE,
                                             (ex, ey, elem_size, elem_size), 3,
                                             border_radius=8)
                else:
                    pygame.draw.rect(screen, MID_GRAY, (ex, ey, elem_size, elem_size),
                                     border_radius=8)
                    if ch_type == "memory_numbers":
                        q_text = self.fonts["large"].render("?", True, DARK_GRAY)
                        q_rect = q_text.get_rect(center=(ex + elem_size // 2,
                                                          ey + elem_size // 2))
                        screen.blit(q_text, q_rect)

        elif phase == "input":
            input_timer = challenge.get("input_timer", 10)
            timer_ratio = max(0, time_remaining / input_timer)
            timer_color = HP_GREEN if timer_ratio > 0.5 else HP_RED
            pygame.draw.rect(screen, DARK_GRAY, (20, menu_y + 8, SCREEN_WIDTH - 40, 8),
                             border_radius=4)
            fill_w = int((SCREEN_WIDTH - 40) * timer_ratio)
            if timer_ratio <= 0.25 and int(time.time() * 6) % 2:
                fill_w = 0
            pygame.draw.rect(screen, timer_color,
                             (20, menu_y + 8, fill_w, 8), border_radius=4)

            title = self.fonts["medium"].render("Repita a sequência!", True, UI_HIGHLIGHT)
            screen.blit(title, title.get_rect(centerx=SCREEN_WIDTH // 2, y=menu_y + 22))

            if ch_type == "memory_numbers":
                elem_size = 50
                gap = 10
                total_width = len(sequence) * (elem_size + gap) - gap
                start_x = SCREEN_WIDTH // 2 - total_width // 2

                for i in range(len(sequence)):
                    ex = start_x + i * (elem_size + gap)
                    ey = menu_y + 55

                    if i < len(player_input):
                        pygame.draw.rect(screen, UI_ACCENT, (ex, ey, elem_size, elem_size),
                                         border_radius=8)
                        num_text = self.fonts["large"].render(str(player_input[i]), True, BLACK)
                        num_rect = num_text.get_rect(center=(ex + elem_size // 2,
                                                              ey + elem_size // 2))
                        screen.blit(num_text, num_rect)
                    else:
                        pygame.draw.rect(screen, MID_GRAY, (ex, ey, elem_size, elem_size),
                                         border_radius=8)
                        if i == len(player_input):
                            pygame.draw.rect(screen, UI_HIGHLIGHT,
                                             (ex, ey, elem_size, elem_size), 2,
                                             border_radius=8)

                hint = self.fonts["small"].render("Use os números do teclado (1-9)", True,
                                                   LIGHT_GRAY)
                screen.blit(hint, hint.get_rect(centerx=SCREEN_WIDTH // 2, y=menu_y + 120))
            else:
                color_options = list(self.memory_colors_map.keys())
                color_names = challenge.get("color_names", {})
                btn_width = 80
                total_w = len(color_options) * (btn_width + 8)
                start_x = SCREEN_WIDTH // 2 - total_w // 2

                for i, cc in enumerate(color_options):
                    bx = start_x + i * (btn_width + 8)
                    by = menu_y + 60
                    color = self.memory_colors_map[cc]
                    pygame.draw.rect(screen, color, (bx, by, btn_width, 40), border_radius=6)
                    label = self.fonts["small"].render(color_names.get(cc, cc), True, WHITE)
                    lr = label.get_rect(center=(bx + btn_width // 2, by + 20))
                    screen.blit(label, lr)

                    key_text = self.fonts["small"].render(str(i + 1), True, UI_TEXT)
                    screen.blit(key_text, (bx + btn_width // 2 - 4, by + 44))

                prog_text = self.fonts["small"].render(
                    f"Progresso: {len(player_input)}/{len(sequence)}", True, UI_ACCENT
                )
                screen.blit(prog_text, prog_text.get_rect(centerx=SCREEN_WIDTH // 2,
                                                           y=menu_y + 115))

                hint = self.fonts["small"].render("Pressione 1-6 para as cores", True,
                                                   LIGHT_GRAY)
                screen.blit(hint, hint.get_rect(centerx=SCREEN_WIDTH // 2, y=menu_y + 140))

    def draw_message_box(self, screen, messages):
        """Draw message box at bottom of screen. Always covers the full
        bottom panel so stale content never bleeds through."""
        menu_y = BATTLE_PANEL_Y
        pygame.draw.rect(screen, UI_BG, (0, menu_y, SCREEN_WIDTH, SCREEN_HEIGHT - menu_y))
        pygame.draw.line(screen, UI_BORDER, (0, menu_y),
                         (SCREEN_WIDTH, menu_y), 2)

        if not messages:
            hint = self.fonts["small"].render("Pressione ENTER para continuar", True,
                                              MID_GRAY)
            screen.blit(hint, hint.get_rect(centerx=SCREEN_WIDTH // 2,
                                            y=menu_y + SCREEN_HEIGHT // 2 - 60))
            return

        msg = messages[0]
        msg_surf = self.fonts["medium"].render(msg, True, UI_TEXT)
        screen.blit(msg_surf, (30, menu_y + 20))

        if int(time.time() * 3) % 2:
            arrow = self.fonts["medium"].render("▼", True, UI_HIGHLIGHT)
            screen.blit(arrow, (SCREEN_WIDTH - 40, SCREEN_HEIGHT - 30))

    def draw_item_menu(self, screen, inventory, selected):
        """Draw item selection menu."""
        menu_y = BATTLE_PANEL_Y
        self._draw_panel_background(screen, menu_y)

        title = self.fonts["medium"].render("Itens:", True, UI_HIGHLIGHT)
        screen.blit(title, (30, menu_y + 10))

        items = [i for i in BATTLE_ITEMS]  # ordered battle-usable items
        for i, item_id in enumerate(items):
            item = ITEMS_DB[item_id]
            qty = inventory.get(item_id, 0)
            by = menu_y + 38 + i * 38

            if i == selected:
                hover = pygame.Surface((440, 32), pygame.SRCALPHA)
                pygame.draw.rect(hover, (*UI_BORDER, 140), (0, 0, 440, 32), border_radius=4)
                screen.blit(hover, (25, by - 2))
                arrow = self.fonts["medium"].render("►", True, UI_HIGHLIGHT)
                screen.blit(arrow, (32, by))

            color = UI_TEXT if qty > 0 else MID_GRAY
            text = self.fonts["medium"].render(f"{item['name']} x{qty}", True, color)
            screen.blit(text, (50, by))

            desc_text = self.fonts["small"].render(item["description"], True, LIGHT_GRAY)
            screen.blit(desc_text, (240, by + 5))

        hint = self.fonts["small"].render("ENTER: Usar  |  ESC: Voltar", True, LIGHT_GRAY)
        screen.blit(hint, (30, SCREEN_HEIGHT - 25))

    def draw_result_overlay(self, screen, correct, message=""):
        """Draw result flash overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((50, 200, 80, 40) if correct else (200, 50, 50, 40))
        screen.blit(overlay, (0, 0))

        if message:
            msg_surf = self.fonts["title"].render(message, True, WHITE)
            shadow = self.fonts["title"].render(message, True, BLACK)
            cx = SCREEN_WIDTH // 2
            cy = SCREEN_HEIGHT // 2
            screen.blit(shadow, shadow.get_rect(center=(cx + 2, cy + 2)))
            screen.blit(msg_surf, msg_surf.get_rect(center=(cx, cy)))

    def draw_victory_screen(self, screen, xp_gained, leveled_up, monster):
        """Draw victory overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        title = self.fonts["title"].render("VITÓRIA!", True, UI_HIGHLIGHT)
        screen.blit(title, title.get_rect(centerx=SCREEN_WIDTH // 2, y=150))

        xp_text = self.fonts["large"].render(f"+{xp_gained} XP", True, XP_BLUE)
        screen.blit(xp_text, xp_text.get_rect(centerx=SCREEN_WIDTH // 2, y=220))

        if leveled_up:
            lvl_text = self.fonts["large"].render(
                f"{monster.name} subiu para Nv.{monster.level}!", True, HP_GREEN
            )
            screen.blit(lvl_text, lvl_text.get_rect(centerx=SCREEN_WIDTH // 2, y=270))

        hint = self.fonts["medium"].render("Pressione ENTER para continuar", True, LIGHT_GRAY)
        if int(time.time() * 2) % 2:
            screen.blit(hint, hint.get_rect(centerx=SCREEN_WIDTH // 2, y=400))

    def draw_defeat_screen(self, screen):
        """Draw defeat overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = self.fonts["title"].render("DERROTA...", True, HP_RED)
        screen.blit(title, title.get_rect(centerx=SCREEN_WIDTH // 2, y=200))

        hint = self.fonts["medium"].render("Seus MathMons serão curados.", True, LIGHT_GRAY)
        screen.blit(hint, hint.get_rect(centerx=SCREEN_WIDTH // 2, y=280))

        cont = self.fonts["medium"].render("Pressione ENTER", True, LIGHT_GRAY)
        if int(time.time() * 2) % 2:
            screen.blit(cont, cont.get_rect(centerx=SCREEN_WIDTH // 2, y=400))

    # ─── Effects / animation helpers ────────────────────────────────

    def sync_hp(self, player_mon, enemy_mon):
        """Feed current HP targets so bars can tween smoothly."""
        self._target_hp["player"] = float(player_mon.current_hp)
        self._target_hp["enemy"] = float(enemy_mon.current_hp)
        if self._display_hp["player"] is None:
            self._display_hp["player"] = float(player_mon.current_hp)
        if self._display_hp["enemy"] is None:
            self._display_hp["enemy"] = float(enemy_mon.current_hp)

    def update(self, dt):
        """Update animation timers, particles and HP tween."""
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

        # HP bars tween toward target (exponentially smoothed)
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
            pop["y"] -= 34 * dt
            if pop["life"] <= 0:
                self.damage_popups.remove(pop)

    def trigger_shake(self, duration=0.3):
        self.shake_timer = duration

    def trigger_flash(self, duration=0.2):
        self.flash_timer = duration

    def trigger_hit(self, duration=0.25):
        """White flash on the enemy after a landed hit."""
        self.hit_flash_timer = duration

    def _burst(self, x, y, color, count=14, speed=160):
        """Spawn a radial particle burst."""
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed_ = random.uniform(speed * 0.4, speed)
            self.particles.append({
                "x": x, "y": y,
                "vx": math.cos(angle) * speed_,
                "vy": math.sin(angle) * speed_ - 40,
                "life": random.uniform(0.25, 0.6),
                "gravity": 260.0,
                "color": color,
                "size": random.uniform(2, 4),
            })

    def add_hit_particles(self, x, y):
        self._burst(x, y, (255, 230, 120), count=16, speed=190)
        self._burst(x, y, (255, 120, 80), count=10, speed=120)

    def add_confetti(self):
        """Confetti rain for the victory screen."""
        colors = [FIRE_COLOR, WATER_COLOR, PLANT_COLOR, ELECTRIC_COLOR,
                  UI_HIGHLIGHT, UI_ACCENT, (255, 255, 255)]
        for _ in range(60):
            self.particles.append({
                "x": random.uniform(0, SCREEN_WIDTH),
                "y": random.uniform(-40, SCREEN_HEIGHT * 0.4),
                "vx": random.uniform(-30, 30),
                "vy": random.uniform(20, 90),
                "life": random.uniform(1.0, 2.6),
                "gravity": 35.0,
                "color": colors[int(random.uniform(0, len(colors)))],
                "size": random.uniform(3, 6),
            })

    def spawn_damage_popup(self, x, y, amount, color=WHITE):
        """Show a floating damage number."""
        if amount <= 0:
            return
        self.damage_popups.append({
            "x": x, "y": y,
            "text": f"-{amount}",
            "life": 0.9,
            "color": color,
        })

    def _draw_popups(self, screen):
        """Draw damage popups and particles (screen-space)."""
        for pop in self.damage_popups:
            alpha = int(255 * min(1.0, pop["life"] / 0.5))
            surf = self.fonts["medium"].render(pop["text"], True, pop["color"])
            surf.set_alpha(alpha)
            screen.blit(surf, (pop["x"] - surf.get_width() // 2, pop["y"] - 20))

        for p in self.particles:
            alpha = int(255 * min(1.0, p["life"] / 0.3))
            surf = pygame.Surface((int(p["size"]) * 2, int(p["size"]) * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*p["color"], alpha),
                               (int(p["size"]), int(p["size"])), int(p["size"]))
            screen.blit(surf, (int(p["x"]) - int(p["size"]), int(p["y"]) - int(p["size"])))

    def get_enemy_center(self):
        return self.ENEMY_HIT_POS

    def get_player_center(self):
        return self.PLAYER_HIT_POS

# MathMon RPG - HUD
import pygame
from settings import *
from utils.sprite_generator import SpriteGenerator


class HUD:
    """Heads-up display for the overworld."""

    def __init__(self, game):
        self.game = game
        self.sprite_gen = SpriteGenerator()

    def draw(self, screen, player_data, current_map_name):
        """Draw the HUD overlay."""
        team = player_data.get("team", [])
        if not team:
            return

        font_med = self.game.fonts.get("medium_bold", self.game.fonts.get("medium"))
        font_small = self.game.fonts.get("small_bold", self.game.fonts.get("small"))
        font_regular = self.game.fonts.get("small", self.game.fonts["small"])

        # Map name
        map_names = {
            "vila": "Vila Raiz",
            "floresta": "Floresta Enigma",
            "caverna": "Caverna Profunda",
            "arena": "Arena Final",
        }
        map_name = map_names.get(current_map_name, current_map_name)
        name_surf = font_med.render(map_name, True, UI_HIGHLIGHT)
        name_bg = pygame.Surface((name_surf.get_width() + 24, 34), pygame.SRCALPHA)
        pygame.draw.rect(name_bg, (*UI_BG, 220), (0, 0, name_bg.get_width(), 34), border_radius=6)
        pygame.draw.rect(name_bg, UI_BORDER, (0, 0, name_bg.get_width(), 34), 2, border_radius=6)
        screen.blit(name_bg, (15, 15))
        screen.blit(name_surf, (27, 20))

        # Team mini display
        for i, monster in enumerate(team):
            x = 15 + i * 36
            y = 56

            # Mini HP indicator (colored circle)
            hp_ratio = monster.current_hp / monster.max_hp if monster.max_hp > 0 else 0
            if hp_ratio > 0.5:
                color = HP_GREEN
                border = (100, 255, 150)
            elif hp_ratio > 0.25:
                color = HP_YELLOW
                border = (255, 230, 100)
            else:
                color = HP_RED
                border = (255, 120, 120)

            if monster.is_fainted():
                color = (50, 50, 60)
                border = MID_GRAY

            # Outer ring
            pygame.draw.circle(screen, UI_BORDER, (x + 12, y + 12), 14)
            pygame.draw.circle(screen, UI_BG, (x + 12, y + 12), 12)
            # Inner color
            pygame.draw.circle(screen, color, (x + 12, y + 12), 10)

            # Highlight
            pygame.draw.circle(screen, border, (x + 12, y + 12), 10, 2)
            pygame.draw.circle(screen, (255, 255, 255, 150), (x + 8, y + 8), 3)

        # Player Level, Title & Badges
        level = player_data.get("player_level", 1)
        title = player_data.get("player_title", "Aprendiz")
        badges = player_data.get("progress", {}).get("badges", 0)
        badge_text = f"  ★ {badges}" if badges > 0 else ""
        player_text = f"Nv. {level} - {title}{badge_text}"

        p_surf = font_small.render(player_text, True, UI_TEXT)
        p_bg = pygame.Surface((p_surf.get_width() + 20, 28), pygame.SRCALPHA)
        pygame.draw.rect(p_bg, (*UI_BG, 220), (0, 0, p_bg.get_width(), 28), border_radius=6)
        pygame.draw.rect(p_bg, UI_BORDER, (0, 0, p_bg.get_width(), 28), 1, border_radius=6)
        screen.blit(p_bg, (SCREEN_WIDTH - p_bg.get_width() - 15, 15))
        screen.blit(p_surf, (SCREEN_WIDTH - p_bg.get_width() - 5, 20))

        # Controls hint bar with backdrop for clear readability
        hint_text = "WASD/Setas: Mover  |  Z/Enter: Interagir  |  X/Esc: Menu"
        hint = font_regular.render(hint_text, True, (215, 220, 235))
        hint_bg = pygame.Surface((hint.get_width() + 18, 22), pygame.SRCALPHA)
        pygame.draw.rect(hint_bg, (15, 18, 28, 180), (0, 0, hint_bg.get_width(), 22), border_radius=5)
        pygame.draw.rect(hint_bg, (50, 60, 85, 180), (0, 0, hint_bg.get_width(), 22), 1, border_radius=5)

        hint_x = SCREEN_WIDTH // 2 - hint_bg.get_width() // 2
        hint_y = SCREEN_HEIGHT - 26
        screen.blit(hint_bg, (hint_x, hint_y))
        screen.blit(hint, (hint_x + 9, hint_y + 3))

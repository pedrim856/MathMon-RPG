# MathMon RPG - Menu UI
import pygame
import time
import math
from settings import *


class PauseMenu:
    """Pause/status menu."""

    def __init__(self, game):
        self.game = game
        self.selected = 0
        self.options = ["Equipe", "Itens", "Salvar", "Voltar"]

    def handle_events(self, events):
        """Handle menu input. Returns action or None."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key in (pygame.K_RETURN, pygame.K_z):
                    return self.options[self.selected].lower()
                elif event.key in (pygame.K_ESCAPE, pygame.K_x):
                    return "voltar"
        return None

    def draw(self, screen, player_data):
        """Draw the pause menu."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        # Menu panel
        panel_w = 250
        panel_h = 250
        panel_x = SCREEN_WIDTH - panel_w - 20
        panel_y = 20

        pygame.draw.rect(screen, UI_BG, (panel_x, panel_y, panel_w, panel_h), border_radius=10)
        pygame.draw.rect(screen, UI_BORDER, (panel_x, panel_y, panel_w, panel_h), 2,
                         border_radius=10)

        # Options
        for i, opt in enumerate(self.options):
            oy = panel_y + 20 + i * 50

            if i == self.selected:
                pygame.draw.rect(screen, UI_BORDER,
                                 (panel_x + 10, oy - 5, panel_w - 20, 40), border_radius=6)
                color = UI_HIGHLIGHT
                # Arrow
                arrow = self.game.fonts["medium"].render("►", True, UI_HIGHLIGHT)
                screen.blit(arrow, (panel_x + 15, oy + 2))
            else:
                color = UI_TEXT

            text = self.game.fonts["medium"].render(opt, True, color)
            screen.blit(text, (panel_x + 40, oy + 4))

        # Team info panel
        team = player_data.get("team", [])
        if team:
            info_x = 20
            info_y = 20
            info_w = SCREEN_WIDTH - panel_w - 60
            info_h = panel_h

            pygame.draw.rect(screen, UI_BG, (info_x, info_y, info_w, info_h), border_radius=10)
            pygame.draw.rect(screen, UI_BORDER, (info_x, info_y, info_w, info_h), 2,
                             border_radius=10)

            title = self.game.fonts["medium"].render("Equipe:", True, UI_HIGHLIGHT)
            screen.blit(title, (info_x + 15, info_y + 10))

            from utils.sprite_generator import SpriteGenerator
            sprite_gen = SpriteGenerator()

            for i, mon in enumerate(team):
                my = info_y + 40 + i * 50

                # Mini sprite
                mini = sprite_gen.get_monster_sprite(mon.monster_id, 32, mon.is_shiny)
                screen.blit(mini, (info_x + 15, my))

                # Name and level
                name_text = self.game.fonts["small"].render(
                    f"{mon.name} Nv.{mon.level}", True, UI_TEXT
                )
                screen.blit(name_text, (info_x + 55, my + 2))

                # HP bar
                hp_bar = sprite_gen.get_hp_bar(mon.current_hp, mon.max_hp, 150, 8)
                screen.blit(hp_bar, (info_x + 55, my + 22))

                hp_text = self.game.fonts["small"].render(
                    f"{mon.current_hp}/{mon.max_hp}", True, LIGHT_GRAY
                )
                screen.blit(hp_text, (info_x + 210, my + 18))


class StarterSelectMenu:
    """Menu for selecting starter MathMon."""

    def __init__(self, game):
        self.game = game
        self.selected = 0
        self.starters = [
            {"id": "flamix", "name": "Flamix", "type": "fogo",
             "desc": "Tipo Fogo. Alto ataque, defesa média."},
            {"id": "aquiel", "name": "Aquiel", "type": "agua",
             "desc": "Tipo Água. HP alto, boa defesa."},
            {"id": "folhex", "name": "Folhex", "type": "planta",
             "desc": "Tipo Planta. Equilibrado em tudo."},
        ]

    def handle_events(self, events):
        """Returns selected starter id or None."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.selected = (self.selected - 1) % len(self.starters)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.selected = (self.selected + 1) % len(self.starters)
                elif event.key in (pygame.K_RETURN, pygame.K_z):
                    return self.starters[self.selected]["id"]
        return None

    def draw(self, screen):
        """Draw starter selection screen."""
        # Background
        screen.fill(BATTLE_BG)

        # Title
        title = self.game.fonts["title"].render("Escolha seu MathMon!", True, UI_HIGHLIGHT)
        screen.blit(title, title.get_rect(centerx=SCREEN_WIDTH // 2, y=30))

        subtitle = self.game.fonts["medium"].render(
            "Use ← → para escolher e ENTER para confirmar", True, LIGHT_GRAY
        )
        screen.blit(subtitle, subtitle.get_rect(centerx=SCREEN_WIDTH // 2, y=80))

        from utils.sprite_generator import SpriteGenerator
        sprite_gen = SpriteGenerator()

        type_colors = {
            "fogo": FIRE_COLOR, "agua": WATER_COLOR,
            "planta": PLANT_COLOR, "eletrico": ELECTRIC_COLOR,
        }

        card_width = 160
        total_width = len(self.starters) * (card_width + 15) - 15
        start_x = SCREEN_WIDTH // 2 - total_width // 2

        for i, starter in enumerate(self.starters):
            cx = start_x + i * (card_width + 15)
            cy = 140
            card_h = 320

            is_selected = i == self.selected
            border_color = type_colors.get(starter["type"], UI_BORDER)

            # Card background
            if is_selected:
                pygame.draw.rect(screen, (*border_color, 40),
                                 (cx - 5, cy - 5, card_width + 10, card_h + 10), border_radius=12)

            pygame.draw.rect(screen, UI_BG, (cx, cy, card_width, card_h), border_radius=10)
            pygame.draw.rect(screen, border_color if is_selected else UI_BORDER,
                             (cx, cy, card_width, card_h), 3 if is_selected else 1,
                             border_radius=10)

            # Monster sprite
            sprite = sprite_gen.get_monster_sprite(starter["id"], 96)
            sprite_x = cx + card_width // 2 - 48
            sprite_y = cy + 15
            if is_selected:
                sprite_y += int(math.sin(time.time() * 3) * 5)
            screen.blit(sprite, (sprite_x, sprite_y))

            # Name
            name_text = self.game.fonts["medium"].render(starter["name"], True,
                                                          border_color if is_selected else UI_TEXT)
            screen.blit(name_text,
                        name_text.get_rect(centerx=cx + card_width // 2, y=cy + 120))

            # Type
            type_text = self.game.fonts["small"].render(
                starter["type"].upper(), True, border_color
            )
            screen.blit(type_text,
                        type_text.get_rect(centerx=cx + card_width // 2, y=cy + 148))

            # Description (word wrap)
            if is_selected:
                words = starter["desc"].split(' ')
                lines = []
                line = ""
                for w in words:
                    test = line + (" " if line else "") + w
                    if self.game.fonts["small"].size(test)[0] < card_width - 20:
                        line = test
                    else:
                        lines.append(line)
                        line = w
                if line:
                    lines.append(line)

                for j, ln in enumerate(lines):
                    desc_surf = self.game.fonts["small"].render(ln, True, LIGHT_GRAY)
                    screen.blit(desc_surf,
                                desc_surf.get_rect(centerx=cx + card_width // 2,
                                                    y=cy + 175 + j * 18))

            # Selection indicator
            if is_selected:
                arrow = self.game.fonts["large"].render("▲", True, UI_HIGHLIGHT)
                screen.blit(arrow,
                            arrow.get_rect(centerx=cx + card_width // 2, y=cy + card_h + 10))

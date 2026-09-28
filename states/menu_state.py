# MathMon RPG - Menu State (Title Screen)
import pygame
import math
import time
from game import GameState
from settings import *
from utils.sprite_generator import SpriteGenerator
from utils.sound import SoundGenerator


class MenuState(GameState):
    """Title screen / main menu."""

    def __init__(self):
        super().__init__()
        self.selected = 0
        self.options = ["Novo Jogo", "Continuar", "Sair"]
        self.sprite_gen = SpriteGenerator()
        self.sound = SoundGenerator()
        self.title_y_offset = 0
        self.particles = []
        self.has_save = False

        # Generate particles
        import random
        for _ in range(50):
            self.particles.append({
                "x": random.randint(0, SCREEN_WIDTH),
                "y": random.randint(0, SCREEN_HEIGHT),
                "speed": random.uniform(0.3, 1.5),
                "size": random.randint(1, 3),
                "color": random.choice([FIRE_COLOR, WATER_COLOR, PLANT_COLOR, ELECTRIC_COLOR]),
                "phase": random.uniform(0, math.pi * 2),
            })

    def on_enter(self, **kwargs):
        from utils.save_system import SaveSystem
        self.has_save = SaveSystem.has_save()
        self.selected = 0
        self.sound.play_music("menu")

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected = (self.selected - 1) % len(self.options)
                    self.sound.play("menu_select")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected = (self.selected + 1) % len(self.options)
                    self.sound.play("menu_select")
                elif event.key in (pygame.K_RETURN, pygame.K_z):
                    self.sound.play("menu_confirm")
                    self._select_option()

    def _select_option(self):
        option = self.options[self.selected]
        if option == "Novo Jogo":
            self.game.player_data = {
                "name": "Jogador",
                "player_level": 1,
                "player_xp": 0,
                "player_title": "Aprendiz",
                "team": [],
                "inventory": {"pocao": 5, "super_pocao": 1, "livro": 1},
                "progress": {"badges": 0, "defeated_trainers": [], "story_flags": []},
                "current_map": "vila",
                "position": [15, 20],
                "direction": "down",
                "needs_starter": True,
            }
            self.game.change_state(STATE_OVERWORLD)
        elif option == "Continuar":
            if self.has_save:
                from utils.save_system import SaveSystem
                from entities.monster import Monster
                save = SaveSystem.load_game()
                if save:
                    team = []
                    for mon_data in save.get("team", []):
                        team.append(Monster.from_dict(mon_data))
                    self.game.player_data = {
                        "name": save["player"]["name"],
                        "team": team,
                        "inventory": save.get("inventory", {"pocao": 3}),
                        "progress": save.get("progress", {"badges": 0, "defeated_trainers": [],
                                                           "story_flags": []}),
                        "current_map": save["player"]["current_map"],
                        "position": save["player"]["position"],
                        "direction": save["player"].get("direction", "down"),
                        "player_level": save["player"].get("player_level", 1),
                        "player_xp": save["player"].get("player_xp", 0),
                        "player_title": save["player"].get("player_title", "Aprendiz"),
                        "needs_starter": False,
                    }
                    self.game.change_state(STATE_OVERWORLD)
        elif option == "Sair":
            self.game.running = False

    def update(self, dt):
        self.title_y_offset = math.sin(time.time() * 2) * 8
        # Update particles
        for p in self.particles:
            p["y"] -= p["speed"]
            p["x"] += math.sin(time.time() * 2 + p["phase"]) * 0.5
            if p["y"] < -10:
                p["y"] = SCREEN_HEIGHT + 10
                import random
                p["x"] = random.randint(0, SCREEN_WIDTH)

    def draw(self, screen):
        # Background gradient
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(15 + 20 * ratio)
            g = int(10 + 15 * ratio)
            b = int(30 + 25 * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Particles
        for p in self.particles:
            alpha_surf = pygame.Surface((p["size"] * 2, p["size"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surf, (*p["color"], 100), (p["size"], p["size"]), p["size"])
            screen.blit(alpha_surf, (int(p["x"]), int(p["y"])))

        # Title
        title_text = "MathMon RPG"
        title_surf = self.game.fonts["huge"].render(title_text, True, UI_HIGHLIGHT)
        # Shadow
        shadow = self.game.fonts["huge"].render(title_text, True, (40, 30, 60))
        screen.blit(shadow, shadow.get_rect(centerx=SCREEN_WIDTH // 2 + 3,
                                             y=83 + self.title_y_offset))
        screen.blit(title_surf, title_surf.get_rect(centerx=SCREEN_WIDTH // 2,
                                                      y=80 + self.title_y_offset))

        # Subtitle
        sub = self.game.fonts["medium"].render("Batalha de Raciocínio!", True, UI_ACCENT)
        screen.blit(sub, sub.get_rect(centerx=SCREEN_WIDTH // 2, y=155 + self.title_y_offset))

        # Monster showcase
        t = time.time()
        showcase = ["flamix", "aquiel", "folhex"]
        for i, mon_id in enumerate(showcase):
            sprite = self.sprite_gen.get_monster_sprite(mon_id, 64)
            mx = 140 + i * 160
            my = 200 + math.sin(t * 2 + i * 1.5) * 10
            screen.blit(sprite, (mx, my))

        # Menu options
        for i, option in enumerate(self.options):
            oy = 370 + i * 55

            is_disabled = (option == "Continuar" and not self.has_save)

            if i == self.selected and not is_disabled:
                # Selected box
                box_w = 250
                box_h = 45
                box_x = SCREEN_WIDTH // 2 - box_w // 2
                pygame.draw.rect(screen, UI_BORDER, (box_x, oy - 5, box_w, box_h),
                                 border_radius=8)
                pygame.draw.rect(screen, UI_HIGHLIGHT, (box_x, oy - 5, box_w, box_h), 2,
                                 border_radius=8)
                color = UI_HIGHLIGHT
                # Arrow
                arrow = self.game.fonts["medium"].render("►", True, UI_HIGHLIGHT)
                screen.blit(arrow, (box_x + 10, oy + 4))
            else:
                color = LIGHT_GRAY if not is_disabled else MID_GRAY

            text = self.game.fonts["large"].render(option, True, color)
            screen.blit(text, text.get_rect(centerx=SCREEN_WIDTH // 2, y=oy + 2))

        # Footer
        footer = self.game.fonts["small"].render("Use ↑↓ e ENTER para selecionar", True, MID_GRAY)
        screen.blit(footer, footer.get_rect(centerx=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT - 30))

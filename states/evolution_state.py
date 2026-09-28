# MathMon RPG - Evolution State
import pygame
import math
import time
from game import GameState
from settings import *
from utils.sprite_generator import SpriteGenerator
from utils.sound import SoundGenerator


class EvolutionState(GameState):
    """Evolution animation state."""

    def __init__(self):
        super().__init__()
        self.sprite_gen = SpriteGenerator()
        self.sound = SoundGenerator()
        self.monster = None
        self.old_name = ""
        self.new_name = ""
        self.old_sprite = None
        self.new_sprite = None
        self.phase = "start"  # start, evolving, done
        self.timer = 0
        self.flash_count = 0

    def on_enter(self, **kwargs):
        self.monster = kwargs.get("monster")
        self.old_name = kwargs.get("old_name", "")
        self.new_name = self.monster.name if self.monster else ""
        self.old_sprite = kwargs.get("old_sprite")
        self.new_sprite = self.sprite_gen.get_monster_sprite(
            self.monster.monster_id, 128, self.monster.is_shiny) if self.monster else None
        self.phase = "start"
        self.timer = 0
        self.flash_count = 0
        self.sound.play("evolution")

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.phase == "done":
                    if event.key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                        self.game.pop_state()

    def update(self, dt):
        self.timer += dt

        if self.phase == "start" and self.timer > 2.0:
            self.phase = "evolving"
            self.timer = 0
        elif self.phase == "evolving" and self.timer > 3.0:
            self.phase = "done"
            self.timer = 0

    def draw(self, screen):
        screen.fill(BLACK)

        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40

        if self.phase == "start":
            # Show old monster
            if self.old_sprite:
                screen.blit(self.old_sprite,
                            self.old_sprite.get_rect(center=(cx, cy)))
            text = self.game.fonts["large"].render(
                f"Quê?! {self.old_name} está evoluindo!", True, UI_HIGHLIGHT
            )
            screen.blit(text, text.get_rect(centerx=cx, y=cy + 100))

        elif self.phase == "evolving":
            # Flashing between old and new
            flash = int(self.timer * 8) % 2
            if flash and self.new_sprite:
                # Scale effect
                scale = 1.0 + math.sin(self.timer * 5) * 0.2
                w = int(128 * scale)
                h = int(128 * scale)
                scaled = pygame.transform.scale(self.new_sprite, (w, h))
                screen.blit(scaled, scaled.get_rect(center=(cx, cy)))
            elif self.old_sprite:
                screen.blit(self.old_sprite,
                            self.old_sprite.get_rect(center=(cx, cy)))

            # White flash
            if int(self.timer * 10) % 3 == 0:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, 100))
                screen.blit(overlay, (0, 0))

        elif self.phase == "done":
            # Show new monster
            if self.new_sprite:
                # Gentle bounce
                offset_y = int(math.sin(time.time() * 3) * 5)
                screen.blit(self.new_sprite,
                            self.new_sprite.get_rect(center=(cx, cy + offset_y)))

            text = self.game.fonts["large"].render(
                f"{self.old_name} evoluiu para {self.new_name}!", True, UI_HIGHLIGHT
            )
            screen.blit(text, text.get_rect(centerx=cx, y=cy + 100))

            hint = self.game.fonts["medium"].render("Pressione ENTER", True, LIGHT_GRAY)
            if int(time.time() * 2) % 2:
                screen.blit(hint, hint.get_rect(centerx=cx, y=cy + 160))

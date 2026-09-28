# MathMon RPG - Text Box UI
import pygame
import time
from settings import *


class TextBox:
    """Pokémon-style text box with typing effect."""

    def __init__(self, game):
        self.game = game
        self.messages = []
        self.current_msg = ""
        self.display_text = ""
        self.char_index = 0
        self.char_timer = 0
        self.char_speed = 0.03  # seconds per character
        self.active = False
        self.finished_typing = False

    def show(self, messages):
        """Show a series of messages."""
        if isinstance(messages, str):
            messages = [messages]
        self.messages = list(messages)
        self.active = True
        self._next_message()

    def _next_message(self):
        """Start displaying next message."""
        if self.messages:
            self.current_msg = self.messages.pop(0)
            self.display_text = ""
            self.char_index = 0
            self.char_timer = 0
            self.finished_typing = False
        else:
            self.active = False

    def advance(self):
        """Advance to next message or finish current one."""
        if not self.finished_typing:
            # Show all text immediately
            self.display_text = self.current_msg
            self.finished_typing = True
        else:
            self._next_message()

    def update(self, dt):
        """Update typing animation."""
        if not self.active or self.finished_typing:
            return

        self.char_timer += dt
        while self.char_timer >= self.char_speed and self.char_index < len(self.current_msg):
            self.char_timer -= self.char_speed
            self.char_index += 1
            self.display_text = self.current_msg[:self.char_index]

        if self.char_index >= len(self.current_msg):
            self.finished_typing = True

    def draw(self, screen):
        """Draw the text box."""
        if not self.active:
            return

        box_height = 100
        box_y = SCREEN_HEIGHT - box_height - 10
        box_x = 10
        box_width = SCREEN_WIDTH - 20

        # Box background with shadow
        shadow_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 100), (4, 4, box_width, box_height), border_radius=12)
        screen.blit(shadow_surf, (box_x, box_y))

        box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(box_surf, (*UI_BG, 240), (0, 0, box_width, box_height), border_radius=12)
        pygame.draw.rect(box_surf, UI_BORDER, (0, 0, box_width, box_height), 3, border_radius=12)
        pygame.draw.rect(box_surf, (255, 255, 255, 30), (3, 3, box_width - 6, box_height - 6), 1, border_radius=9) # Inner glow
        screen.blit(box_surf, (box_x, box_y))

        # Text
        font = self.game.fonts["medium"]
        # Word wrap
        words = self.display_text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test = current_line + (" " if current_line else "") + word
            if font.size(test)[0] < box_width - 40:
                current_line = test
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        for i, line in enumerate(lines[:3]):
            text_surf = font.render(line, True, UI_TEXT)
            screen.blit(text_surf, (box_x + 20, box_y + 15 + i * 28))

        # Blinking arrow when done typing
        if self.finished_typing:
            if int(time.time() * 3) % 2:
                arrow = self.game.fonts["medium"].render("▼", True, UI_HIGHLIGHT)
                screen.blit(arrow, (box_x + box_width - 35, box_y + box_height - 30))

    def is_active(self):
        return self.active

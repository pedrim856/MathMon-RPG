# MathMon RPG - Game Engine
import pygame
from settings import *


class Game:
    """Main game class - manages the game loop and state machine."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0

        # State machine
        self.states = {}
        self.current_state = None
        self.state_stack = []

        # Shared game data
        self.player_data = None
        self.fonts = {}
        self._load_fonts()

    def _load_fonts(self):
        """Load game fonts with preferred modern system font."""
        available = pygame.font.get_fonts()
        font_name = None
        for name in ["segoeui", "arial", "trebuchetms", "verdana", "dejavusans"]:
            if name in available:
                font_name = name
                break

        if font_name:
            self.fonts = {
                "tiny": pygame.font.SysFont(font_name, 16),
                "small": pygame.font.SysFont(font_name, 20),
                "small_bold": pygame.font.SysFont(font_name, 20, bold=True),
                "medium": pygame.font.SysFont(font_name, 26),
                "medium_bold": pygame.font.SysFont(font_name, 26, bold=True),
                "large": pygame.font.SysFont(font_name, 34, bold=True),
                "title": pygame.font.SysFont(font_name, 48, bold=True),
                "huge": pygame.font.SysFont(font_name, 64, bold=True),
            }
        else:
            self.fonts = {
                "tiny": pygame.font.Font(None, 18),
                "small": pygame.font.Font(None, 22),
                "small_bold": pygame.font.Font(None, 22),
                "medium": pygame.font.Font(None, 28),
                "medium_bold": pygame.font.Font(None, 28),
                "large": pygame.font.Font(None, 36),
                "title": pygame.font.Font(None, 56),
                "huge": pygame.font.Font(None, 72),
            }

    def register_state(self, name, state):
        """Register a game state."""
        self.states[name] = state
        state.game = self

    def change_state(self, name, **kwargs):
        """Change to a different state."""
        if self.current_state and hasattr(self.current_state, 'on_exit'):
            self.current_state.on_exit()
        self.current_state = self.states[name]
        if hasattr(self.current_state, 'on_enter'):
            self.current_state.on_enter(**kwargs)

    def push_state(self, name, **kwargs):
        """Push a state onto the stack (for overlays like dialogs)."""
        if self.current_state:
            self.state_stack.append(self.current_state)
        self.current_state = self.states[name]
        if hasattr(self.current_state, 'on_enter'):
            self.current_state.on_enter(**kwargs)

    def pop_state(self):
        """Pop the current state and return to previous."""
        if hasattr(self.current_state, 'on_exit'):
            self.current_state.on_exit()
        if self.state_stack:
            self.current_state = self.state_stack.pop()
            if hasattr(self.current_state, 'on_resume'):
                self.current_state.on_resume()
        else:
            self.running = False

    def run(self):
        """Main game loop."""
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0

            # Handle events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    return

            # Update current state
            if self.current_state:
                self.current_state.handle_events(events)
                self.current_state.update(self.dt)
                self.current_state.draw(self.screen)

            pygame.display.flip()

        pygame.quit()


class GameState:
    """Base class for game states."""

    def __init__(self):
        self.game = None

    def on_enter(self, **kwargs):
        pass

    def on_exit(self):
        pass

    def on_resume(self):
        pass

    def handle_events(self, events):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass

# MathMon RPG - Settings & Constants
import os

# Display
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "MathMon RPG - Batalha de Raciocínio!"

# Tile
TILE_SIZE = 32

# Map dimensions (in tiles)
MAP_WIDTH = 30
MAP_HEIGHT = 25

# Player
PLAYER_SPEED = 3
ENCOUNTER_CHANCE = 0.03  # 3% chance per step on tall grass

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (30, 30, 40)
LIGHT_GRAY = (200, 200, 215)
MID_GRAY = (110, 110, 125)

# UI Colors
UI_BG = (20, 22, 35)
UI_BORDER = (95, 105, 140)
UI_TEXT = (245, 245, 250)
UI_HIGHLIGHT = (255, 180, 50) # Vibrant Gold
UI_ACCENT = (50, 200, 255)   # Cyan

# Battle Colors
BATTLE_BG = (25, 25, 38)
HP_GREEN = (46, 204, 113)
HP_YELLOW = (241, 196, 15)
HP_RED = (231, 76, 60)
XP_BLUE = (52, 152, 219)

# Type Colors
FIRE_COLOR = (255, 87, 34)
WATER_COLOR = (33, 150, 243)
PLANT_COLOR = (76, 175, 80)
ELECTRIC_COLOR = (255, 193, 7)
TERRA_COLOR = (139, 90, 43)
GELO_COLOR = (128, 222, 234)
LOGICO_COLOR = (156, 39, 176)
CAOS_COLOR = (96, 125, 139)

# Menu Colors
MENU_BG = (15, 16, 28)
MENU_BORDER = (75, 85, 120)
MENU_SELECT = (255, 180, 50)

# Tile IDs
TILE_GRASS = 0
TILE_TALL_GRASS = 1
TILE_PATH = 2
TILE_WATER = 3
TILE_TREE = 4
TILE_ROCK = 5
TILE_HOUSE = 6
TILE_DOOR = 7
TILE_SAND = 8
TILE_CAVE_FLOOR = 9
TILE_CAVE_WALL = 10
TILE_PORTAL = 11
TILE_SIGN = 12
TILE_FLOWER = 13
TILE_FENCE = 14
TILE_ARENA_FLOOR = 15

# Solid tiles (can't walk through)
SOLID_TILES = {TILE_WATER, TILE_TREE, TILE_ROCK, TILE_HOUSE, TILE_CAVE_WALL, TILE_FENCE}

# Encounter tiles
ENCOUNTER_TILES = {TILE_TALL_GRASS, TILE_CAVE_FLOOR}

# Game States
STATE_MENU = "menu"
STATE_OVERWORLD = "overworld"
STATE_BATTLE = "battle"
STATE_EVOLUTION = "evolution"

# Battle states
BSTATE_INTRO = "intro"
BSTATE_PLAYER_TURN = "player_turn"
BSTATE_MOVE_SELECT = "move_select"
BSTATE_CHALLENGE = "challenge"
BSTATE_ITEM_SELECT = "item_select"
BSTATE_PLAYER_RESULT = "player_attack_result"
BSTATE_ENEMY_TURN = "enemy_turn"
BSTATE_ENEMY_RESULT = "enemy_attack"
BSTATE_VICTORY = "victory"
BSTATE_DEFEAT = "defeat"
BSTATE_RUN = "run"

# Battle UI layout anchors (bottom panels share a consistent baseline)
BATTLE_PANEL_Y = 380          # Standard bottom panel top (action/move/item/message)
BATTLE_CHALLENGE_Y = 360      # Challenge overlay top

# Battle feel tuning
PLAYER_ATTACK_DAMAGE_MULT = 2.5   # keeps battles to ~5 correct answers
ENEMY_ACCURACY_BASE = 0.6
ENEMY_ACCURACY_MAX = 0.85
ENEMY_INTRO_SLIDE_TIME = 0.6      # seconds for enemy to slide into scene
CHALLENGE_WARNING_TIME = 3.0      # seconds remaining before timer warning sound

# Challenge Types
CHALLENGE_MATH = "math"
CHALLENGE_EQUATION = "equation"
CHALLENGE_MEMORY = "memory"
CHALLENGE_LOGIC = "logic"

# Difficulty scaling
DIFFICULTY_LEVELS = {
    1: {"math_range": (1, 10), "ops": ["+", "-"], "timer": 15},
    2: {"math_range": (1, 20), "ops": ["+", "-", "×"], "timer": 14},
    3: {"math_range": (1, 30), "ops": ["+", "-", "×"], "timer": 13},
    4: {"math_range": (2, 40), "ops": ["+", "-", "×", "÷"], "timer": 12},
    5: {"math_range": (5, 50), "ops": ["+", "-", "×", "÷"], "timer": 11},
    6: {"math_range": (5, 60), "ops": ["+", "-", "×", "÷"], "timer": 10},
    7: {"math_range": (10, 80), "ops": ["+", "-", "×", "÷"], "timer": 9},
    8: {"math_range": (10, 99), "ops": ["+", "-", "×", "÷"], "timer": 8},
    9: {"math_range": (15, 120), "ops": ["+", "-", "×", "÷"], "timer": 7},
    10: {"math_range": (20, 150), "ops": ["+", "-", "×", "÷"], "timer": 6},
}

# XP curve
def xp_for_level(level):
    """XP needed to reach next level"""
    return int((4 * (level ** 3)) / 5)

# Save file path
SAVE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(SAVE_DIR, "save_data.json")

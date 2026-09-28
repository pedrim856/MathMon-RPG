# MathMon RPG - Save System
import json
import os
from settings import SAVE_FILE


class SaveSystem:
    """Handles saving and loading game progress."""

    @staticmethod
    def save_game(player_data):
        """Save game data to JSON file."""
        save_data = {
            "player": {
                "name": player_data.get("name", "Jogador"),
                "position": player_data.get("position", [5, 5]),
                "current_map": player_data.get("current_map", "vila"),
                "direction": player_data.get("direction", "down"),
                "player_level": player_data.get("player_level", 1),
                "player_xp": player_data.get("player_xp", 0),
                "player_title": player_data.get("player_title", "Aprendiz"),
            },
            "team": [],
            "inventory": player_data.get("inventory", {"pocao": 3, "super_pocao": 0, "livro": 1}),
            "progress": player_data.get("progress", {
                "badges": 0,
                "defeated_trainers": [],
                "story_flags": [],
            }),
        }

        # Save team monsters
        for monster in player_data.get("team", []):
            mon_data = {
                "monster_id": monster.monster_id,
                "name": monster.name,
                "level": monster.level,
                "current_hp": monster.current_hp,
                "xp": monster.xp,
            }
            save_data["team"].append(mon_data)

        try:
            with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Erro ao salvar: {e}")
            return False

    @staticmethod
    def load_game():
        """Load game data from JSON file."""
        if not os.path.exists(SAVE_FILE):
            return None
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar: {e}")
            return None

    @staticmethod
    def has_save():
        """Check if a save file exists."""
        return os.path.exists(SAVE_FILE)

    @staticmethod
    def delete_save():
        """Delete save file."""
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)

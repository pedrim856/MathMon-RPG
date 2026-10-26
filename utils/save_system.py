# MathMon RPG - Save System
import json
import os
import shutil
from settings import SAVE_FILE

BACKUP_SAVE_FILE = SAVE_FILE.replace(".json", "_backup.json")
TMP_SAVE_FILE = SAVE_FILE.replace(".json", ".tmp")


class SaveSystem:
    """Handles robust saving, loading, backup, and recovery of game progress."""

    @staticmethod
    def validate_save_data(data):
        """Validate that save structure contains all essential fields."""
        if not isinstance(data, dict):
            return False
        required_keys = {"player", "team", "inventory", "progress"}
        if not required_keys.issubset(data.keys()):
            return False
        player = data.get("player", {})
        if not isinstance(player, dict) or "current_map" not in player:
            return False
        return True

    @staticmethod
    def save_game(player_data):
        """Save game data atomically with backup creation."""
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
            # 1. Create a backup of existing valid save
            if os.path.exists(SAVE_FILE):
                try:
                    shutil.copy2(SAVE_FILE, BACKUP_SAVE_FILE)
                except Exception:
                    pass

            # 2. Atomic write via temporary file
            with open(TMP_SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            os.replace(TMP_SAVE_FILE, SAVE_FILE)
            return True
        except Exception as e:
            print(f"Erro ao salvar: {e}")
            if os.path.exists(TMP_SAVE_FILE):
                try:
                    os.remove(TMP_SAVE_FILE)
                except Exception:
                    pass
            return False

    @staticmethod
    def load_game():
        """Load game data from JSON file with automatic fallback to backup."""
        # Try primary save file first
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if SaveSystem.validate_save_data(data):
                    return data
            except Exception as e:
                print(f"Erro ao carregar save principal, tentando backup: {e}")

        # Fallback to backup save file
        if os.path.exists(BACKUP_SAVE_FILE):
            try:
                with open(BACKUP_SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if SaveSystem.validate_save_data(data):
                    return data
            except Exception as e:
                print(f"Erro ao carregar backup: {e}")

        return None

    @staticmethod
    def has_save():
        """Check if a valid save or backup file exists."""
        return os.path.exists(SAVE_FILE) or os.path.exists(BACKUP_SAVE_FILE)

    @staticmethod
    def delete_save():
        """Delete save and backup files."""
        for path in (SAVE_FILE, BACKUP_SAVE_FILE, TMP_SAVE_FILE):
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass

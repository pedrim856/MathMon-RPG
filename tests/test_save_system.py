import unittest
import os
import json
from utils.save_system import SaveSystem, SAVE_FILE, BACKUP_SAVE_FILE, TMP_SAVE_FILE
from entities.monster import Monster


class TestSaveSystem(unittest.TestCase):
    """Unit tests for SaveSystem validation and atomic save/load routines."""

    def setUp(self):
        # Stash existing save file if present
        self.original_save = None
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                self.original_save = f.read()

    def tearDown(self):
        # Restore original save file
        SaveSystem.delete_save()
        if self.original_save is not None:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                f.write(self.original_save)

    def test_validation(self):
        """Test save data structure validation."""
        self.assertFalse(SaveSystem.validate_save_data(None))
        self.assertFalse(SaveSystem.validate_save_data({}))
        self.assertFalse(SaveSystem.validate_save_data({"player": {}}))

        valid_sample = {
            "player": {"name": "Test", "current_map": "vila"},
            "team": [],
            "inventory": {},
            "progress": {},
        }
        self.assertTrue(SaveSystem.validate_save_data(valid_sample))

    def test_save_and_load_roundtrip(self):
        """Test saving player data and loading it back."""
        player_data = {
            "name": "Ash",
            "position": [10, 12],
            "current_map": "floresta",
            "direction": "up",
            "player_level": 3,
            "player_xp": 45,
            "player_title": "Desbravador",
            "team": [Monster("flamix", level=7)],
            "inventory": {"pocao": 4},
            "progress": {"badges": 1, "defeated_trainers": ["t1"], "story_flags": []},
        }

        success = SaveSystem.save_game(player_data)
        self.assertTrue(success)
        self.assertTrue(SaveSystem.has_save())

        loaded = SaveSystem.load_game()
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["player"]["name"], "Ash")
        self.assertEqual(loaded["player"]["current_map"], "floresta")
        self.assertEqual(len(loaded["team"]), 1)
        self.assertEqual(loaded["team"][0]["monster_id"], "flamix")
        self.assertEqual(loaded["progress"]["badges"], 1)

    def test_corrupted_save_backup_recovery(self):
        """Test that if the primary save is corrupted, the system falls back to backup."""
        player_data = {
            "name": "Hero",
            "position": [5, 5],
            "current_map": "vila",
            "team": [],
            "inventory": {},
            "progress": {},
        }
        SaveSystem.save_game(player_data)
        # Second save creates the backup
        player_data["player_title"] = "Mestre"
        SaveSystem.save_game(player_data)

        # Corrupt the primary save file with broken JSON
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            f.write("CORRUPTED_JSON_DATA{{{")

        loaded = SaveSystem.load_game()
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["player"]["name"], "Hero")


if __name__ == "__main__":
    unittest.main()

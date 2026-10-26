import unittest
from entities.monster import Monster
from data.monsters_db import MONSTERS_DB


class TestMonsterEntity(unittest.TestCase):
    """Unit tests for Monster entity and battle attributes."""

    def test_monster_initialization(self):
        """Test monster initialization and baseline stats."""
        mon = Monster("flamix", level=5)
        self.assertEqual(mon.name, "Flamix")
        self.assertEqual(mon.level, 5)
        self.assertEqual(mon.current_hp, mon.max_hp)
        self.assertGreater(mon.max_hp, 0)
        self.assertGreater(mon.atk, 0)
        self.assertGreater(mon.defense, 0)
        self.assertGreater(mon.speed, 0)

    def test_damage_and_healing(self):
        """Test HP deduction, capping at 0, and healing."""
        mon = Monster("aquiel", level=5)
        initial_hp = mon.current_hp
        dealt = mon.take_damage(20)
        self.assertEqual(dealt, 20)
        self.assertEqual(mon.current_hp, initial_hp - 20)

        mon.heal(10)
        self.assertEqual(mon.current_hp, initial_hp - 10)

        mon.heal(1000)
        self.assertEqual(mon.current_hp, mon.max_hp)

    def test_fainting(self):
        """Test monster fainted state when HP reaches 0."""
        mon = Monster("terrox", level=5)
        self.assertFalse(mon.is_fainted())
        mon.take_damage(mon.max_hp + 50)
        self.assertTrue(mon.is_fainted())
        self.assertEqual(mon.current_hp, 0)

    def test_type_effectiveness(self):
        """Test elemental advantages from TYPE_CHART."""
        self.assertGreater(Monster.type_effectiveness("agua", "fogo"), 1.0)
        self.assertGreater(Monster.type_effectiveness("fogo", "planta"), 1.0)
        self.assertLess(Monster.type_effectiveness("fogo", "agua"), 1.0)
        self.assertEqual(Monster.type_effectiveness("fogo", "desconhecido"), 1.0)


if __name__ == "__main__":
    unittest.main()

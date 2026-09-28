# MathMon RPG - Monster Entity
import random
from settings import xp_for_level, PLAYER_ATTACK_DAMAGE_MULT
from data.monsters_db import MONSTERS_DB, TYPE_CHART
from data.moves_db import MOVES_DB


class Monster:
    """Represents a MathMon creature."""

    def __init__(self, monster_id, level=5, custom_name=None, is_shiny=False):
        self.monster_id = monster_id
        data = MONSTERS_DB[monster_id]

        self.name = custom_name or data["name"]
        self.base_name = data["name"]
        self.type = data["type"]
        self.level = level
        self.xp = 0
        self.is_shiny = is_shiny

        # Base stats
        self.base_hp = data["base_hp"]
        self.base_atk = data["base_atk"]
        self.base_def = data["base_def"]
        self.base_spd = data["base_spd"]

        # Calculated stats
        self._calculate_stats()
        self.current_hp = self.max_hp

        # Evolution
        self.evolves_to = data.get("evolves_to")
        self.evolves_at = data.get("evolves_at")

        # Moves
        self.move_ids = list(data.get("moves", []))[:4]
        self.description = data.get("description", "")

    def _calculate_stats(self):
        """Calculate stats based on level."""
        level_mult = 1 + (self.level - 1) * 0.08
        self.max_hp = int(self.base_hp * level_mult) + self.level * 2
        self.atk = int(self.base_atk * level_mult)
        self.defense = int(self.base_def * level_mult)
        self.speed = int(self.base_spd * level_mult)

    def get_moves(self):
        """Get move data for this monster's moves."""
        moves = []
        for move_id in self.move_ids:
            if move_id in MOVES_DB:
                move = dict(MOVES_DB[move_id])
                move["id"] = move_id
                moves.append(move)
        return moves

    def take_damage(self, amount):
        """Take damage. Returns actual damage dealt."""
        actual = min(amount, self.current_hp)
        self.current_hp = max(0, self.current_hp - amount)
        return actual

    def heal(self, amount):
        """Heal HP."""
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    def is_fainted(self):
        """Check if monster has fainted."""
        return self.current_hp <= 0

    def gain_xp(self, amount):
        """Gain XP. Returns True if leveled up."""
        self.xp += amount
        leveled = False
        while self.xp >= xp_for_level(self.level) and self.level < 50:
            self.xp -= xp_for_level(self.level)
            self.level += 1
            old_max_hp = self.max_hp
            self._calculate_stats()
            # Heal the HP gained from leveling
            self.current_hp += (self.max_hp - old_max_hp)
            leveled = True
        return leveled

    @staticmethod
    def type_effectiveness(move_type, target_type):
        """Type multiplier for a move against a target type (1.0 if neutral)."""
        if move_type in TYPE_CHART and target_type in TYPE_CHART[move_type]:
            return TYPE_CHART[move_type][target_type]
        return 1.0

    def can_evolve(self):
        """Check if monster can evolve."""
        return (self.evolves_to is not None and
                self.evolves_at is not None and
                self.level >= self.evolves_at)

    def evolve(self):
        """Evolve the monster. Returns new monster_id or None."""
        if not self.can_evolve():
            return None

        new_id = self.evolves_to
        new_data = MONSTERS_DB[new_id]

        was_custom_name = self.name != self.base_name
        self.monster_id = new_id
        self.base_name = new_data["name"]
        # Keep a custom nickname, otherwise adopt the evolved name
        self.name = self.name if was_custom_name else new_data["name"]

        self.type = new_data["type"]
        self.base_hp = new_data["base_hp"]
        self.base_atk = new_data["base_atk"]
        self.base_def = new_data["base_def"]
        self.base_spd = new_data["base_spd"]
        self.evolves_to = new_data.get("evolves_to")
        self.evolves_at = new_data.get("evolves_at")
        self.move_ids = list(new_data.get("moves", []))[:4]
        self.description = new_data.get("description", "")

        old_max = self.max_hp
        self._calculate_stats()
        self.current_hp = min(self.current_hp + (self.max_hp - old_max), self.max_hp)

        return new_id

    def calculate_damage(self, move, target, correct, time_bonus=1.0):
        """Calculate damage for an attack.

        Args:
            move: Move data dict
            target: Target Monster
            correct: Whether the challenge was answered correctly
            time_bonus: Bonus multiplier for fast answers (1.0-2.0)

        Returns: damage amount
        """
        if not correct:
            return 0

        power = move["power"]
        attack = self.atk
        defense = target.defense

        # Base damage formula
        damage = ((2 * self.level / 5 + 2) * power * attack / defense) / 50 + 2

        # Type effectiveness
        move_type = move.get("type", "normal")
        damage *= Monster.type_effectiveness(move_type, target.type)

        # STAB (Same Type Attack Bonus)
        if move_type == self.type:
            damage *= 1.3

        # Time bonus
        damage *= time_bonus

        # Random variation (90-110%)
        damage *= random.uniform(0.9, 1.1)

        # Keep battles short: ends in at most ~5 correct answers
        damage *= PLAYER_ATTACK_DAMAGE_MULT

        return max(1, int(damage))

    @staticmethod
    def get_xp_reward(defeated_monster, is_trainer=False, perfect_battle=False):
        """Calculate XP reward for defeating a monster."""
        base_xp = 30 + defeated_monster.level * 8
        xp = int((base_xp * defeated_monster.level) / 7)
        if is_trainer:
            xp = int(xp * 1.5)
        if perfect_battle:
            xp = int(xp * 1.15)
        return max(1, xp)

    def to_dict(self):
        """Serialize monster to dict for saving."""
        return {
            "monster_id": self.monster_id,
            "name": self.name,
            "level": self.level,
            "current_hp": self.current_hp,
            "xp": self.xp,
            "is_shiny": self.is_shiny,
        }

    @staticmethod
    def from_dict(data):
        """Create monster from saved dict."""
        mon = Monster(data["monster_id"], data["level"], data.get("name"), data.get("is_shiny", False))
        mon.current_hp = data.get("current_hp", mon.max_hp)
        mon.xp = data.get("xp", 0)
        return mon

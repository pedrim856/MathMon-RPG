# MathMon RPG - Battle Engine
import random
import time
from settings import (
    BSTATE_INTRO, BSTATE_PLAYER_TURN, BSTATE_MOVE_SELECT, BSTATE_CHALLENGE,
    BSTATE_ITEM_SELECT, BSTATE_PLAYER_RESULT, BSTATE_ENEMY_TURN,
    BSTATE_ENEMY_RESULT, BSTATE_VICTORY, BSTATE_DEFEAT, BSTATE_RUN,
    ENEMY_ACCURACY_BASE, ENEMY_ACCURACY_MAX,
)
from entities.monster import Monster
from data.questions_db import QuestionGenerator
from data.moves_db import MOVES_DB
from data.items_db import ITEMS_DB


class BattleEngine:
    """Manages battle logic, turns, and damage calculation."""

    def __init__(self, player_team, enemy_team, is_wild=True, trainer_data=None):
        self.player_team = player_team
        self.enemy_team = enemy_team
        self.is_wild = is_wild
        self.trainer_data = trainer_data

        # Current active monsters
        self.player_monster = self._get_first_alive(player_team)
        self.enemy_monster = self._get_first_alive(enemy_team)

        # Battle state
        self.state = BSTATE_INTRO
        self.turn_count = 0
        self.messages = []
        self.current_move = None
        self.current_challenge = None
        self.challenge_start_time = 0
        self.player_answer = ""
        self.battle_result = None  # "win", "lose", "run"
        self.xp_gained = 0
        self.leveled_up = False
        self.can_evolve = False
        self.defending = False
        self.perfect_battle = True

        # Damage tracking (used by the UI for effects/popups)
        self.last_player_damage = 0
        self.last_enemy_damage = 0
        self.last_correct = False

        # Memory challenge state
        self.memory_phase = "show"  # show, input
        self.memory_index = 0
        self.memory_input = []
        self.memory_show_timer = 0
        self.memory_correct = False

    def _get_first_alive(self, team):
        """Get first non-fainted monster."""
        for mon in team:
            if not mon.is_fainted():
                return mon
        return None

    def start_battle(self):
        """Initialize battle."""
        self.state = BSTATE_INTRO
        name = self.trainer_data.get("name", "Treinador") if self.trainer_data else "Treinador"
        if self.is_wild:
            self.messages = [f"Um {self.enemy_monster.name} selvagem apareceu!"]
        else:
            self.messages = [f"{name} quer batalhar!",
                             f"{name} enviou {self.enemy_monster.name}!"]
        self.messages.append(f"Vai, {self.player_monster.name}!")

    @property
    def trainer_name(self):
        """Name of the opposing trainer (or generic label)."""
        if self.trainer_data:
            return self.trainer_data.get("name", "Treinador")
        return "Treinador"

    def advance_intro(self):
        """Advance intro messages."""
        if self.messages:
            self.messages.pop(0)
        if not self.messages:
            self.state = BSTATE_PLAYER_TURN

    def get_player_moves(self):
        """Get available moves for player monster."""
        return self.player_monster.get_moves()

    def select_action(self, action):
        """Player selects an action."""
        if action == "attack":
            self.state = BSTATE_MOVE_SELECT
        elif action == "defend":
            self.defending = True
            self.messages = [f"{self.player_monster.name} se defendeu!"]
            self.state = BSTATE_ENEMY_TURN
        elif action == "item":
            self.state = BSTATE_ITEM_SELECT
        elif action == "run":
            if self.is_wild:
                if random.random() < 0.7:
                    self.messages = ["Fugiu com sucesso!"]
                    self.state = BSTATE_RUN
                    self.battle_result = "run"
                else:
                    self.messages = ["Não conseguiu fugir!"]
                    self.state = BSTATE_ENEMY_TURN
            else:
                self.messages = ["Não pode fugir de uma batalha com treinador!"]
                self.state = BSTATE_PLAYER_TURN

    def select_move(self, move_index):
        """Player selects a move."""
        moves = self.get_player_moves()
        if 0 <= move_index < len(moves):
            self.current_move = moves[move_index]
            self._generate_challenge()

    def _generate_challenge(self):
        """Generate a challenge for the selected move."""
        challenge_type = self.current_move["challenge_type"]
        difficulty = max(1, min(10, self.player_monster.level // 5 + 1))
        self.current_challenge = QuestionGenerator.generate(challenge_type, difficulty)
        self.challenge_start_time = time.time()
        self.player_answer = ""
        self.state = BSTATE_CHALLENGE

        if self.current_challenge["type"].startswith("memory"):
            self.memory_phase = "show"
            self.memory_index = 0
            self.memory_input = []
            self.memory_show_timer = 0
            self.memory_correct = False

    def _apply_player_attack(self, correct, time_bonus=1.0):
        """Resolve a (correct/incorrect) player attack and set messages."""
        damage = 0
        self.last_player_damage = 0
        self.last_correct = bool(correct)
        mon = self.player_monster
        move = self.current_move
        target = self.enemy_monster

        if correct:
            damage = mon.calculate_damage(move, target, True, time_bonus)
            target.take_damage(damage)
            self.last_player_damage = damage

            effect = Monster.type_effectiveness(move.get("type", "normal"), target.type)
            messages = [f"{mon.name} usou {move['name']}!"]
            if time_bonus > 1.3:
                messages.insert(0, "Resposta rápida! Dano bônus!")
            if effect >= 2.0:
                messages.append("Ataque super efetivo!")
            elif effect <= 0.5:
                messages.append("Não foi muito efetivo...")
            messages.append(f"Causou {damage} de dano!")
            self.messages = messages
        else:
            self.perfect_battle = False
            self.messages = [
                "Errado! ✗",
                f"A resposta era: {self.current_challenge['answer']}",
                f"{mon.name} errou o ataque!",
            ]

        # Check if enemy fainted
        if target.is_fainted():
            self._handle_enemy_defeated()
        else:
            self.state = BSTATE_PLAYER_RESULT
            self.defending = False

    def submit_answer(self, answer=None):
        """Submit an answer to the current challenge."""
        if self.state != BSTATE_CHALLENGE:
            return

        if answer is None:
            answer = self.player_answer

        correct = str(answer).strip() == str(self.current_challenge["answer"]).strip()

        time_bonus = 1.0
        if correct:
            elapsed = time.time() - self.challenge_start_time
            timer = self.current_challenge.get("timer", 10)
            time_ratio = max(0, 1 - elapsed / timer)
            time_bonus = 1.0 + time_ratio * 0.5  # 1.0 to 1.5x

        self._apply_player_attack(correct, time_bonus)

    def submit_memory_answer(self, sequence):
        """Submit memory challenge answer."""
        if self.state != BSTATE_CHALLENGE:
            return

        correct = sequence == self.current_challenge["answer"]
        self.memory_correct = correct

        time_bonus = 1.0
        if correct:
            elapsed = time.time() - self.challenge_start_time
            timer = self.current_challenge.get("input_timer", 10)
            time_ratio = max(0, 1 - elapsed / timer)
            time_bonus = 1.0 + time_ratio * 0.5

        self._apply_player_attack(correct, time_bonus)

    def _handle_enemy_defeated(self):
        """Handle when enemy monster is defeated."""
        next_enemy = None
        if not self.is_wild:
            for mon in self.enemy_team:
                if not mon.is_fainted() and mon != self.enemy_monster:
                    next_enemy = mon
                    break

        if next_enemy:
            self.enemy_monster = next_enemy
            self.messages.append(f"{self.trainer_name} enviou {next_enemy.name}!")
            self.state = BSTATE_PLAYER_RESULT
        else:
            # Victory!
            xp = Monster.get_xp_reward(self.enemy_monster, not self.is_wild, self.perfect_battle)
            self.xp_gained = xp
            self.messages.append(f"{self.enemy_monster.name} foi derrotado!")
            self.messages.append(f"+{xp} XP!")
            self.leveled_up = self.player_monster.gain_xp(xp)
            if self.leveled_up:
                self.messages.append(
                    f"{self.player_monster.name} subiu para o nível {self.player_monster.level}!"
                )
            self.can_evolve = self.player_monster.can_evolve()
            self.state = BSTATE_VICTORY
            self.battle_result = "win"

    def advance_result(self):
        """Advance through result messages to enemy turn."""
        if self.messages:
            self.messages.pop(0)
        if not self.messages:
            if self.state == BSTATE_PLAYER_RESULT:
                self.state = BSTATE_ENEMY_TURN
            elif self.state in (BSTATE_VICTORY, BSTATE_DEFEAT, BSTATE_RUN):
                pass  # Battle over

    def do_enemy_turn(self):
        """Enemy performs their turn."""
        if self.enemy_monster.is_fainted():
            return

        moves = self.enemy_monster.get_moves()
        if not moves:
            self.messages = [f"{self.enemy_monster.name} não sabe o que fazer!"]
            self.state = BSTATE_PLAYER_TURN
            return

        move = random.choice(moves)
        self.last_enemy_damage = 0

        # Enemy "accuracy" based on enemy and player level difference (GDD formula)
        level_diff = self.enemy_monster.level - self.player_monster.level
        accuracy = ENEMY_ACCURACY_BASE + (level_diff * 0.015)
        accuracy = max(0.40, min(accuracy, 0.95))
        hit = random.random() < accuracy

        if hit:
            damage = self.enemy_monster.calculate_damage(move, self.player_monster,
                                                         True, 1.0)
            reduced = self.defending
            if reduced:
                damage = max(1, damage // 2)
            self.player_monster.take_damage(damage)
            self.last_enemy_damage = damage
            self.messages = [
                f"{self.enemy_monster.name} usou {move['name']}!",
                f"Causou {damage} de dano!",
            ]
            if reduced:
                self.messages.append("A defesa reduziu o dano!")
        else:
            self.messages = [
                f"{self.enemy_monster.name} usou {move['name']}!",
                "Mas errou!",
            ]

        self.defending = False

        # Check if player monster fainted
        if self.player_monster.is_fainted():
            next_mon = self._get_first_alive(self.player_team)
            if next_mon:
                self.player_monster = next_mon
                self.messages.append(f"Vai, {next_mon.name}!")
                self.state = BSTATE_ENEMY_RESULT
            else:
                self.messages.append("Todos os seus MathMons foram derrotados!")
                self.state = BSTATE_DEFEAT
                self.battle_result = "lose"
        else:
            self.state = BSTATE_ENEMY_RESULT

    def advance_enemy_result(self):
        """Advance through enemy attack messages."""
        if self.messages:
            self.messages.pop(0)
        if not self.messages:
            if self.state == BSTATE_ENEMY_RESULT:
                self.turn_count += 1
                self.state = BSTATE_PLAYER_TURN
            elif self.state == BSTATE_DEFEAT:
                pass  # Battle over

    def use_item(self, item_name):
        """Use a healing item."""
        item = ITEMS_DB.get(item_name)
        if not item or not item.get("usable_in_battle", False):
            return False
        heal = item.get("heal", 0)
        self.player_monster.heal(heal)
        self.messages = [f"Usou {item['name']}! +{heal} HP"]
        self.state = BSTATE_ENEMY_TURN
        return True

    def is_over(self):
        """Check if battle is over."""
        return self.battle_result is not None
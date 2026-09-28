# MathMon RPG - Battle State
import pygame
import time
from game import GameState
from settings import *
from battle.battle_engine import BattleEngine
from battle.battle_ui import BattleUI
from data.items_db import BATTLE_ITEMS
from utils.sound import SoundGenerator


class BattleState(GameState):
    """Battle state - handles the entire battle flow with effects."""

    def __init__(self):
        super().__init__()
        self.engine = None
        self.ui = None
        self.sound = SoundGenerator()

        # UI state
        self.selected_action = 0
        self.selected_move = 0
        self.selected_item = 0
        self.selected_option = 0
        self.answer_text = ""

        # Animation timing
        self.state_timer = 0
        self.result_display_timer = 0
        self.show_result_overlay = False
        self.result_correct = False
        self.prev_state = None
        self.timer_warned = False

        # Memory challenge
        self.memory_show_timer = 0
        self.memory_show_index = 0
        self.memory_input = []
        self.memory_phase = "show"
        self.memory_input_start_time = 0

        self.input_cooldown = 0

    def on_enter(self, **kwargs):
        """Initialize battle."""
        player_team = self.game.player_data.get("team", [])
        enemy_team = kwargs.get("enemy_team", [])
        is_wild = kwargs.get("is_wild", True)
        trainer_data = kwargs.get("trainer_data", None)

        self.engine = BattleEngine(player_team, enemy_team, is_wild, trainer_data)
        self.ui = BattleUI(self.game)
        self.engine.start_battle()
        self.sound.play("battle_start")
        self.sound.play_music("battle")

        self.selected_action = 0
        self.selected_move = 0
        self.selected_item = 0
        self.selected_option = 0
        self.answer_text = ""
        self.state_timer = 0
        self.show_result_overlay = False
        self.result_correct = False
        self.prev_state = None
        self.timer_warned = False
        self.input_cooldown = 0.3

    def handle_events(self, events):
        if self.input_cooldown > 0:
            return

        state = self.engine.state

        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if state == BSTATE_INTRO:
                if event.key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                    self.engine.advance_intro()
                    self.sound.play("menu_confirm")

            elif state == BSTATE_PLAYER_TURN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_action = (self.selected_action - 2) % 4
                    self.sound.play("menu_select")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_action = (self.selected_action + 2) % 4
                    self.sound.play("menu_select")
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.selected_action = (self.selected_action - 1) % 4
                    self.sound.play("menu_select")
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.selected_action = (self.selected_action + 1) % 4
                    self.sound.play("menu_select")
                elif event.key in (pygame.K_RETURN, pygame.K_z):
                    actions = ["attack", "defend", "item", "run"]
                    self.engine.select_action(actions[self.selected_action])
                    self.sound.play("menu_confirm")
                    if self.engine.state == BSTATE_MOVE_SELECT:
                        self.selected_move = 0

            elif state == BSTATE_MOVE_SELECT:
                moves = self.engine.get_player_moves()
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_move = (self.selected_move - 2) % len(moves)
                    self.sound.play("menu_select")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_move = (self.selected_move + 2) % len(moves)
                    self.sound.play("menu_select")
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.selected_move = (self.selected_move - 1) % len(moves)
                    self.sound.play("menu_select")
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.selected_move = (self.selected_move + 1) % len(moves)
                    self.sound.play("menu_select")
                elif event.key in (pygame.K_RETURN, pygame.K_z):
                    self.engine.select_move(self.selected_move)
                    self.sound.play("menu_confirm")
                    if self.engine.state == BSTATE_CHALLENGE:
                        self.answer_text = ""
                        self.selected_option = 0
                        ch = self.engine.current_challenge
                        if ch["type"].startswith("memory"):
                            self.memory_phase = "show"
                            self.memory_show_index = 0
                            self.memory_show_timer = 0
                            self.memory_input = []
                        else:
                            self.timer_warned = False
                elif event.key == pygame.K_ESCAPE:
                    self.engine.state = BSTATE_PLAYER_TURN
                    self.sound.play("menu_back")

            elif state == BSTATE_CHALLENGE:
                ch = self.engine.current_challenge
                if ch["type"] == "input":
                    self._handle_challenge_input(event)
                elif ch["type"].startswith("memory"):
                    self._handle_memory_input(event)

            elif state == BSTATE_ITEM_SELECT:
                items = BATTLE_ITEMS
                usable = [i for i in items
                          if self.game.player_data.get("inventory", {}).get(i, 0) > 0]
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_item = max(0, self.selected_item - 1)
                    self.sound.play("menu_select")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_item = min(max(0, len(items) - 1),
                                             self.selected_item + 1)
                    self.sound.play("menu_select")
                elif event.key in (pygame.K_RETURN, pygame.K_z):
                    if 0 <= self.selected_item < len(items):
                        item = items[self.selected_item]
                        inv = self.game.player_data.get("inventory", {})
                        if inv.get(item, 0) > 0:
                            self.engine.use_item(item)
                            inv[item] -= 1
                            self.sound.play("correct")
                        else:
                            self.engine.messages = ["Você não tem esse item!"]
                            self.engine.state = BSTATE_PLAYER_TURN
                elif event.key == pygame.K_ESCAPE:
                    self.engine.state = BSTATE_PLAYER_TURN
                    self.sound.play("menu_back")

            elif state == BSTATE_PLAYER_RESULT:
                if event.key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                    self.engine.advance_result()

            elif state == BSTATE_ENEMY_RESULT:
                if event.key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                    self.engine.advance_enemy_result()

            elif state in (BSTATE_VICTORY, BSTATE_DEFEAT, BSTATE_RUN):
                if event.key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                    if self.engine.messages:
                        self.engine.messages.pop(0)
                    else:
                        self._end_battle()

    # ─── Challenge input ────────────────────────────────────────────

    def _handle_challenge_input(self, event):
        """Handle keyboard input for math/equation/logic challenges."""
        options = self.engine.current_challenge.get("options", [])

        if event.key in (pygame.K_RETURN, pygame.K_z):
            if options and 0 <= self.selected_option < len(options):
                submitted = str(options[self.selected_option])
            else:
                submitted = self.answer_text
            self._submit_answer(submitted)

        elif event.key == pygame.K_LEFT:
            if options:
                self.selected_option = (self.selected_option - 1) % len(options)
                self.sound.play("menu_select")
        elif event.key == pygame.K_RIGHT:
            if options:
                self.selected_option = (self.selected_option + 1) % len(options)
                self.sound.play("menu_select")
        elif event.key == pygame.K_BACKSPACE:
            self.answer_text = self.answer_text[:-1]
        elif event.key == pygame.K_MINUS:
            if not self.answer_text:
                self.answer_text = "-"
        else:
            char = event.unicode
            if char and (char.isdigit() or char in "-."):
                if len(self.answer_text) < 10:
                    self.answer_text += char

    def _submit_answer(self, answer):
        """Submit answer, then play result feedback with hit effects."""
        self.engine.submit_answer(answer)
        correct = self.engine.last_correct

        self.show_result_overlay = True
        self.result_correct = correct
        self.result_display_timer = 1.0

        if correct:
            self.sound.play("correct")
            self.ui.trigger_shake()
            self.ui.trigger_hit(0.25)
            self.ui.add_hit_particles(*self.ui.get_enemy_center())
            self.ui.spawn_damage_popup(*self.ui.get_enemy_center(),
                                       self.engine.last_player_damage,
                                       (255, 240, 150))
        else:
            self.sound.play("wrong")

    def _handle_memory_input(self, event):
        """Handle input for memory challenges."""
        ch = self.engine.current_challenge

        if self.memory_phase == "show":
            return

        if event.unicode and event.unicode.isdigit():
            if ch["type"] == "memory_numbers":
                num = int(event.unicode)
                if 1 <= num <= 9:
                    self.memory_input.append(num)
                    self.sound.play("menu_select")
            else:
                color_codes = list(self.ui.memory_colors_map.keys())
                idx = int(event.unicode) - 1
                if 0 <= idx < len(color_codes):
                    self.memory_input.append(color_codes[idx])
                    self.sound.play("menu_select")

            if len(self.memory_input) >= len(ch["sequence"]):
                self.engine.submit_memory_answer(self.memory_input)
                correct = self.engine.memory_correct
                self.show_result_overlay = True
                self.result_correct = correct
                self.result_display_timer = 1.0
                if correct:
                    self.sound.play("correct")
                    self.ui.trigger_shake()
                    self.ui.trigger_hit(0.25)
                    self.ui.add_hit_particles(*self.ui.get_enemy_center())
                    self.ui.spawn_damage_popup(*self.ui.get_enemy_center(),
                                               self.engine.last_player_damage,
                                               (255, 240, 150))
                else:
                    self.sound.play("wrong")

    def _end_battle(self):
        """End the battle, triggering evolution state when applicable."""
        self.engine.last_correct = False
        self.game.player_data["_battle_result"] = self.engine.battle_result

        if self.engine.battle_result == "win":
            # Add XP to player
            if "player_xp" in self.game.player_data:
                from settings import xp_for_level
                xp = getattr(self.engine, "xp_gained", 0)
                self.game.player_data["player_xp"] += xp
                while self.game.player_data["player_xp"] >= xp_for_level(self.game.player_data["player_level"]):
                    self.game.player_data["player_xp"] -= xp_for_level(self.game.player_data["player_level"])
                    self.game.player_data["player_level"] += 1
                    
                    # Update Title
                    lvl = self.game.player_data["player_level"]
                    if lvl < 5: title = "Aprendiz"
                    elif lvl < 10: title = "Estudante"
                    elif lvl < 15: title = "Calculista"
                    elif lvl < 20: title = "Gênio"
                    elif lvl < 30: title = "Mestre"
                    else: title = "Lenda da Matemática"
                    self.game.player_data["player_title"] = title

            mon = self.engine.player_monster
            if self.engine.can_evolve and mon.can_evolve():
                old_id = mon.monster_id
                old_name = mon.name
                old_sprite = self.ui.sprite_gen.get_monster_sprite(old_id, 128, mon.is_shiny)
                mon.evolve()
                self.sound.play_music("overworld")
                self.game.push_state(
                    STATE_EVOLUTION,
                    monster=mon,
                    old_name=old_name,
                    old_sprite=old_sprite,
                )
                return

        self.sound.play_music("overworld")
        self.game.pop_state()

    def update(self, dt):
        self.ui.update(dt)
        self.ui.sync_hp(self.engine.player_monster, self.engine.enemy_monster)

        if self.input_cooldown > 0:
            self.input_cooldown -= dt
            return

        state = self.engine.state

        # One-shot effects on state transitions
        if state != self.prev_state:
            if state == BSTATE_VICTORY:
                self.sound.play("victory")
                self.ui.add_confetti()
                if self.engine.leveled_up:
                    self.sound.play("level_up")
            elif state == BSTATE_DEFEAT:
                self.sound.play("defeat")
            if state == BSTATE_CHALLENGE:
                self.timer_warned = False
            self.prev_state = state

        # Result overlay timer
        if self.show_result_overlay:
            self.result_display_timer -= dt
            if self.result_display_timer <= 0:
                self.show_result_overlay = False

        # Auto-advance enemy turn
        if state == BSTATE_ENEMY_TURN:
            self.state_timer += dt
            if self.state_timer >= 0.8:
                self.state_timer = 0
                self.engine.do_enemy_turn()
                if self.engine.messages and "Causou" in self.engine.messages[0]:
                    self.sound.play("attack_hit")
                    self.ui.trigger_shake(0.2)
                if self.engine.last_enemy_damage > 0:
                    self.ui.spawn_damage_popup(*self.ui.get_player_center(),
                                               self.engine.last_enemy_damage,
                                               (255, 110, 110))

        # Challenge timers
        if state == BSTATE_CHALLENGE:
            ch = self.engine.current_challenge
            if ch["type"].startswith("memory"):
                self._update_memory(dt)
            else:
                elapsed = time.time() - self.engine.challenge_start_time
                timer = ch.get("timer", 10)
                remaining = max(0, timer - elapsed)
                if 0 < remaining <= CHALLENGE_WARNING_TIME and not self.timer_warned:
                    self.sound.play("timer_warning")
                    self.timer_warned = True
                if remaining <= 0:
                    self._submit_answer("__timeout__")

    def _update_memory(self, dt):
        """Update memory challenge display."""
        ch = self.engine.current_challenge
        sequence = ch.get("sequence", [])

        if self.memory_phase == "show":
            self.memory_show_timer += dt
            show_speed = ch.get("timer", 5) / max(1, len(sequence))

            if self.memory_show_timer >= show_speed:
                self.memory_show_timer = 0
                self.memory_show_index += 1
                self.sound.play("timer_tick")

                if self.memory_show_index >= len(sequence):
                    self.memory_phase = "input"
                    self.memory_input = []
                    self.memory_input_start_time = time.time()
        elif self.memory_phase == "input":
            elapsed = time.time() - self.memory_input_start_time
            input_timer = ch.get("input_timer", 10)
            remaining = max(0, input_timer - elapsed)
            if 0 < remaining <= CHALLENGE_WARNING_TIME and not self.timer_warned:
                self.sound.play("timer_warning")
                self.timer_warned = True
            if remaining <= 0:
                self.engine.submit_memory_answer([])
                self.show_result_overlay = True
                self.result_correct = False
                self.result_display_timer = 1.0
                self.sound.play("wrong")

    # ─── Drawing ────────────────────────────────────────────────────

    def draw(self, screen):
        state = self.engine.state

        # Determine background type from the current map
        map_name = self.game.player_data.get("current_map", "vila")
        bg_type = "grass"
        if map_name == "caverna":
            bg_type = "cave"
        elif map_name == "arena":
            bg_type = "arena"

        # Draw battle scene
        self.ui.draw_battle_scene(screen, self.engine.player_monster,
                                   self.engine.enemy_monster, bg_type)

        if state == BSTATE_INTRO:
            self.ui.draw_message_box(screen, self.engine.messages)

        elif state == BSTATE_PLAYER_TURN:
            self.ui.draw_action_menu(screen, self.selected_action)

        elif state == BSTATE_MOVE_SELECT:
            moves = self.engine.get_player_moves()
            self.ui.draw_move_menu(screen, moves, self.selected_move)

        elif state == BSTATE_CHALLENGE:
            ch = self.engine.current_challenge
            if ch["type"].startswith("memory"):
                time_remaining = 0
                if self.memory_phase == "input":
                    elapsed = time.time() - self.memory_input_start_time
                    time_remaining = max(0, ch.get("input_timer", 10) - elapsed)
                self.ui.draw_memory_challenge(
                    screen, ch, self.memory_phase,
                    self.memory_show_index, self.memory_input, time_remaining
                )
            else:
                elapsed = time.time() - self.engine.challenge_start_time
                timer = ch.get("timer", 10)
                time_remaining = max(0, timer - elapsed)
                self.ui.draw_challenge_screen(
                    screen, ch, self.answer_text, time_remaining, self.selected_option
                )

        elif state == BSTATE_ITEM_SELECT:
            self.ui.draw_item_menu(screen, self.game.player_data.get("inventory", {}),
                                    self.selected_item)

        elif state in (BSTATE_PLAYER_RESULT, BSTATE_ENEMY_RESULT):
            self.ui.draw_message_box(screen, self.engine.messages)

        elif state == BSTATE_ENEMY_TURN:
            msg = self.game.fonts["medium"].render(
                f"{self.engine.enemy_monster.name} está pensando...", True, UI_TEXT
            )
            box_y = BATTLE_PANEL_Y
            pygame.draw.rect(screen, UI_BG, (0, box_y, SCREEN_WIDTH, SCREEN_HEIGHT - box_y))
            pygame.draw.line(screen, UI_BORDER, (0, box_y), (SCREEN_WIDTH, box_y), 2)

            # Animated thinking dots
            dots = "." * (1 + int(self.ui.time * 3) % 3)
            hint = self.game.fonts["small"].render(f"Escolhendo ataque{dots}", True,
                                                    LIGHT_GRAY)
            screen.blit(msg, (30, box_y + 20))
            screen.blit(hint, (30, box_y + 55))

        elif state == BSTATE_VICTORY:
            if self.engine.messages:
                self.ui.draw_message_box(screen, self.engine.messages)
            else:
                self.ui.draw_victory_screen(screen, self.engine.xp_gained,
                                             self.engine.leveled_up,
                                             self.engine.player_monster)

        elif state == BSTATE_DEFEAT:
            if self.engine.messages:
                self.ui.draw_message_box(screen, self.engine.messages)
            else:
                self.ui.draw_defeat_screen(screen)

        elif state == BSTATE_RUN:
            self.ui.draw_message_box(screen, self.engine.messages)

        # Result overlay
        if self.show_result_overlay:
            result_msg = "CORRETO!" if self.result_correct else "ERRADO!"
            self.ui.draw_result_overlay(screen, self.result_correct, result_msg)
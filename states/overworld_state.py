# MathMon RPG - Overworld State
import pygame
import random
from game import GameState
from settings import *
from entities.player import Player
from entities.npc import NPC
from entities.monster import Monster
from world.maps import WorldMap
from world.camera import Camera
from ui.hud import HUD
from ui.text_box import TextBox
from ui.menu import PauseMenu, StarterSelectMenu
from data.monsters_db import WILD_ENCOUNTERS, TRAINERS
from data.items_db import ITEMS_DB
from utils.sound import SoundGenerator
from utils.sprite_generator import SpriteGenerator


class OverworldState(GameState):
    """Main exploration state."""

    def __init__(self):
        super().__init__()
        self.world = WorldMap()
        self.player = None
        self.camera = None
        self.npcs = []
        self.hud = None
        self.text_box = None
        self.pause_menu = None
        self.starter_menu = None
        self.sound = SoundGenerator()
        self.sprite_gen = SpriteGenerator()

        # State flags
        self.paused = False
        self.selecting_starter = False
        self.in_dialog = False
        self.current_dialog_npc = None
        self.transition_timer = 0
        self.transition_alpha = 0
        self.transitioning = False
        self.transition_target = None
        self.input_cooldown = 0

        # Trainer data on current map
        self.trainers_on_map = []
        self.pending_trainer_battle = None

    def on_enter(self, **kwargs):
        """Initialize the overworld."""
        pd = self.game.player_data
        self.sound.play_music("overworld")

        # Load map
        map_name = pd.get("current_map", "vila")
        self.world.load_map(map_name)

        # Create player
        pos = pd.get("position", list(self.world.get_map_data()["player_start"]))
        self.player = Player(pos[0], pos[1])
        self.player.direction = pd.get("direction", "down")

        # Camera
        map_data = self.world.get_map_data()
        self.camera = Camera(map_data["width"], map_data["height"])
        self.camera.snap_to(self.player.pixel_x, self.player.pixel_y)

        # NPCs
        self._load_npcs()

        # Trainers
        self._load_trainers()

        # UI
        self.hud = HUD(self.game)
        self.text_box = TextBox(self.game)
        self.pause_menu = PauseMenu(self.game)
        self.starter_menu = StarterSelectMenu(self.game)

        # Check if needs starter
        self.selecting_starter = pd.get("needs_starter", False)
        self.paused = False
        self.in_dialog = False
        self.input_cooldown = 0.3

    def on_resume(self):
        """Called when returning from battle."""
        pd = self.game.player_data
        self.sound.play_music("overworld")

        # Heal team if defeated and return home
        if pd.get("_battle_result") == "lose":
            for mon in pd.get("team", []):
                mon.current_hp = mon.max_hp
            pd["current_map"] = "vila"
            pd["position"] = [15, 20]
            self.on_enter()
        elif pd.get("_battle_result") == "win":
            # Mark trainer as defeated
            trainer_id = pd.get("_defeated_trainer")
            if trainer_id:
                if trainer_id not in pd["progress"]["defeated_trainers"]:
                    pd["progress"]["defeated_trainers"].append(trainer_id)

        pd.pop("_battle_result", None)
        pd.pop("_defeated_trainer", None)
        self.input_cooldown = 0.3

    def _load_npcs(self):
        """Load NPCs for current map."""
        self.npcs = []
        map_data = self.world.get_map_data()
        for npc_data in map_data.get("npcs", []):
            self.npcs.append(NPC(npc_data))

    def _load_trainers(self):
        """Load trainer positions for current map."""
        self.trainers_on_map = []
        map_data = self.world.get_map_data()
        defeated = self.game.player_data.get("progress", {}).get("defeated_trainers", [])
        for trainer_ref in map_data.get("trainers", []):
            t_id = trainer_ref["id"]
            if t_id not in defeated:
                trainer_info = dict(TRAINERS.get(t_id, {}))
                trainer_info["x"] = trainer_ref["x"]
                trainer_info["y"] = trainer_ref["y"]
                trainer_info["id"] = t_id
                self.trainers_on_map.append(trainer_info)

    def handle_events(self, events):
        if self.input_cooldown > 0:
            return

        if self.selecting_starter:
            result = self.starter_menu.handle_events(events)
            if result:
                self._give_starter(result)
            return

        if self.transitioning:
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.in_dialog:
                    if event.key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                        self.text_box.advance()
                        self.sound.play("dialog")
                        if not self.text_box.is_active():
                            self.in_dialog = False
                            # Check if this was a starter-giving NPC
                            if (self.current_dialog_npc and
                                    self.current_dialog_npc.gives_starter and
                                    not self.game.player_data.get("team")):
                                self.selecting_starter = True
                            self.current_dialog_npc = None
                    return

                if self.paused:
                    action = self.pause_menu.handle_events([event])
                    if action:
                        self._handle_pause_action(action)
                    return

                if event.key in (pygame.K_ESCAPE, pygame.K_x):
                    if not self.paused and self.game.player_data.get("team"):
                        self.paused = True
                        return

                if event.key in (pygame.K_RETURN, pygame.K_z):
                    self._try_interact()

    def _try_interact(self):
        """Try to interact with facing object."""
        tilemap = self.world.get_current_tilemap()
        result = self.player.check_interaction(tilemap, self.npcs, self.trainers_on_map)

        if result:
            if result["type"] == "npc":
                npc = result["npc"]
                self.current_dialog_npc = npc
                self.text_box.show(npc.dialog)
                self.in_dialog = True
                self.sound.play("dialog")
            elif result["type"] == "trainer":
                trainer = result["trainer"]
                self._start_trainer_battle(trainer)
            elif result["type"] == "sign":
                self.text_box.show(["Uma placa com informações..."])
                self.in_dialog = True

    def _give_starter(self, monster_id):
        """Give starter monster to player."""
        starter = Monster(monster_id, level=5)
        self.game.player_data["team"] = [starter]
        self.game.player_data["needs_starter"] = False
        self.selecting_starter = False
        self.text_box.show([
            f"Você recebeu {starter.name}!",
            f"{starter.name} será seu parceiro nessa jornada!",
            "Explore o mundo e desafie outros treinadores!",
            "Resolva os desafios para atacar nas batalhas!",
        ])
        self.in_dialog = True

    def _handle_pause_action(self, action):
        """Handle pause menu actions."""
        pd = self.game.player_data
        if action == "voltar":
            self.paused = False
        elif action == "salvar":
            from utils.save_system import SaveSystem
            pd["position"] = [self.player.grid_x, self.player.grid_y]
            pd["direction"] = self.player.direction
            pd["current_map"] = self.world.current_map_name
            if SaveSystem.save_game(pd):
                self.paused = False
                self.text_box.show(["Jogo salvo com sucesso!"])
                self.in_dialog = True
        elif action == "equipe":
            pass  # Team is already shown in the pause panel
        elif action == "itens":
            inv = pd.get("inventory", {})
            own_items = [i for i in ITEMS_DB if inv.get(i, 0) > 0]
            self.paused = False
            if not own_items:
                self.text_box.show(["Seu inventário está vazio!"])
            else:
                lines = ["Seus itens:"]
                for item_id in ITEMS_DB:
                    qty = inv.get(item_id, 0)
                    if qty > 0:
                        lines.append(
                            f"{ITEMS_DB[item_id]['name']} x{qty} - "
                            f"{ITEMS_DB[item_id]['description']}"
                        )
                self.text_box.show(lines)
            self.in_dialog = True

    def _start_wild_battle(self):
        """Start a wild encounter."""
        map_name = self.world.current_map_name
        encounters = WILD_ENCOUNTERS.get(map_name, WILD_ENCOUNTERS["vila"])

        # Weighted random selection
        total_weight = sum(e["weight"] for e in encounters)
        r = random.uniform(0, total_weight)
        current = 0
        chosen = encounters[0]
        for enc in encounters:
            current += enc["weight"]
            if r <= current:
                chosen = enc
                break

        level = random.randint(chosen["level_range"][0], chosen["level_range"][1])
        # 5% chance of being shiny
        is_shiny = random.random() < 0.05
        wild_mon = Monster(chosen["monster_id"], level, is_shiny=is_shiny)

        self.sound.play("battle_start")
        self.game.player_data["_battle_result"] = None
        self.game.push_state(STATE_BATTLE, enemy_team=[wild_mon], is_wild=True)

    def _start_trainer_battle(self, trainer_data):
        """Start a trainer battle."""
        # Build enemy team
        enemy_team = []
        for mon_info in trainer_data.get("team", []):
            enemy_team.append(Monster(mon_info["monster_id"], mon_info["level"]))

        self.sound.play("battle_start")
        self.game.player_data["_battle_result"] = None
        self.game.player_data["_defeated_trainer"] = trainer_data["id"]

        # Show dialog first
        self.text_box.show([trainer_data.get("dialog_before", "Prepare-se para batalhar!")])
        self.in_dialog = True
        self.pending_trainer_battle = {
            "enemy_team": enemy_team,
            "trainer_data": trainer_data,
        }

    def _check_trainer_proximity(self):
        """Check if player is near a trainer (triggers battle)."""
        for trainer in self.trainers_on_map:
            dx = abs(self.player.grid_x - trainer["x"])
            dy = abs(self.player.grid_y - trainer["y"])
            if dx + dy <= 3:  # Within 3 tiles
                self._start_trainer_battle(trainer)
                self.trainers_on_map.remove(trainer)
                return

    def _change_map(self, portal):
        """Transition to a new map."""
        self.transitioning = True
        self.transition_alpha = 0
        self.transition_target = portal

    def _do_map_transition(self):
        """Execute map transition."""
        portal = self.transition_target
        self.world.load_map(portal["target_map"])
        self.player.set_position(portal["target_x"], portal["target_y"])

        map_data = self.world.get_map_data()
        self.camera = Camera(map_data["width"], map_data["height"])
        self.camera.snap_to(self.player.pixel_x, self.player.pixel_y)

        self.game.player_data["current_map"] = portal["target_map"]
        self.game.player_data["position"] = [portal["target_x"], portal["target_y"]]

        self._load_npcs()
        self._load_trainers()

    def update(self, dt):
        if self.input_cooldown > 0:
            self.input_cooldown -= dt
            return

        # Map transition
        if self.transitioning:
            self.transition_alpha += dt * 500
            if self.transition_alpha >= 255:
                self._do_map_transition()
                self.transition_alpha = 255
                self.transitioning = False
                self.transition_timer = 0.5
            return

        if self.transition_timer > 0:
            self.transition_timer -= dt
            self.transition_alpha = max(0, self.transition_alpha - dt * 500)
            return

        if self.selecting_starter or self.paused or self.in_dialog:
            self.text_box.update(dt)

            # Check if dialog ended and we have pending trainer battle
            if not self.in_dialog and self.pending_trainer_battle:
                battle_data = self.pending_trainer_battle
                self.pending_trainer_battle = None
                self.game.push_state(STATE_BATTLE,
                                      enemy_team=battle_data["enemy_team"],
                                      is_wild=False,
                                      trainer_data=battle_data["trainer_data"])
            return

        # Player movement
        if not self.player.moving:
            keys = pygame.key.get_pressed()
            tilemap = self.world.get_current_tilemap()
            self.player.handle_input(keys, tilemap, self.npcs, self.trainers_on_map)

        self.player.update(dt)

        # Camera follow
        self.camera.update(self.player.pixel_x, self.player.pixel_y, dt)

        # Check events when player stops
        if not self.player.moving and self.game.player_data.get("team"):
            tilemap = self.world.get_current_tilemap()

            # Portal check
            portal = self.player.check_portal(tilemap)
            if portal:
                self._change_map(portal)
                return

            # Wild encounter check
            if self.player.steps > 0 and self.player.check_encounter(tilemap):
                self._start_wild_battle()
                return

    def draw(self, screen):
        if self.selecting_starter:
            self.starter_menu.draw(screen)
            return

        # Draw map
        tilemap = self.world.get_current_tilemap()
        tilemap.draw(screen, self.camera)

        # Draw NPCs
        for npc in self.npcs:
            npc.draw(screen, self.camera)

        # Draw trainers
        for trainer in self.trainers_on_map:
            npc_type = trainer.get("npc_type", "trainer")
            sprite = self.sprite_gen.get_npc_sprite(npc_type)
            pos = self.camera.apply((trainer["x"] * TILE_SIZE, trainer["y"] * TILE_SIZE))
            screen.blit(sprite, pos)

        # Draw player
        self.player.draw(screen, self.camera)

        # Draw HUD
        self.hud.draw(screen, self.game.player_data, self.world.current_map_name)

        # Draw text box
        if self.in_dialog:
            self.text_box.draw(screen)

        # Draw pause menu
        if self.paused:
            self.pause_menu.draw(screen, self.game.player_data)

        # Transition overlay
        if self.transition_alpha > 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill(BLACK)
            overlay.set_alpha(int(self.transition_alpha))
            screen.blit(overlay, (0, 0))

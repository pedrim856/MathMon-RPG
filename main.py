# MathMon RPG - Batalha de Raciocínio!
# Um jogo educacional inspirado em Pokémon Fire Red
# Resolva contas matemáticas e jogos de memória para atacar!
#
# Controles:
#   Setas / WASD - Mover
#   Z / Enter   - Confirmar / Interagir
#   X / Escape  - Menu / Voltar
#
# by MathMon Team

import pygame
import sys
import os
# Ensure the script's directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game import Game
from settings import *
from states.menu_state import MenuState
from states.overworld_state import OverworldState
from states.battle_state import BattleState
from states.evolution_state import EvolutionState

def main():
    """Entry point for MathMon RPG."""
    # Create game instance
    game = Game()
    # Register all states
    game.register_state(STATE_MENU, MenuState())
    game.register_state(STATE_OVERWORLD, OverworldState())
    game.register_state(STATE_BATTLE, BattleState())
    game.register_state(STATE_EVOLUTION, EvolutionState())
    # Start at menu
    game.change_state(STATE_MENU)
    # Run the game
    game.run()

if __name__ == "__main__":
    main()
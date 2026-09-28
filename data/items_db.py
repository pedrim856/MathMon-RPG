# MathMon RPG - Items Database

ITEMS_DB = {
    "pocao": {
        "name": "Poção",
        "description": "Recupera 30 HP",
        "heal": 30,
        "usable_in_battle": True,
    },
    "super_pocao": {
        "name": "Super Poção",
        "description": "Recupera 60 HP",
        "heal": 60,
        "usable_in_battle": True,
    },
    "livro": {
        "name": "Livro de Matemática",
        "description": "Um livro sábio...",
        "heal": 0,
        "usable_in_battle": False,
    },
}

# Items the player can use inside a battle (potions, in order shown)
BATTLE_ITEMS = [item_id for item_id in ITEMS_DB if ITEMS_DB[item_id]["usable_in_battle"]]
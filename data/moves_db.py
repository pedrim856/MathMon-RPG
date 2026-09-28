# MathMon RPG - Moves Database
from settings import *

MOVES_DB = {
    # ─── UNIVERSAL ──────────────────────────────────────────────────
    "investida": {
        "name": "Investida",
        "type": "normal",
        "power": 15,
        "challenge_type": CHALLENGE_MATH,
        "description": "Um ataque básico. Resolva uma conta!",
    },

    # ─── FIRE MOVES ─────────────────────────────────────────────────
    "bola_de_fogo": {
        "name": "Bola de Fogo",
        "type": "fogo",
        "power": 25,
        "challenge_type": CHALLENGE_MATH,
        "description": "Lança uma bola de fogo! Resolva a multiplicação!",
    },
    "provocar": {
        "name": "Provocar",
        "type": "fogo",
        "power": 10,
        "challenge_type": CHALLENGE_LOGIC,
        "description": "Provoca o inimigo! Encontre o padrão!",
    },
    "furia": {
        "name": "Fúria",
        "type": "fogo",
        "power": 20,
        "challenge_type": CHALLENGE_MEMORY,
        "description": "Ataque furioso! Memorize a sequência!",
    },
    "chama_furiosa": {
        "name": "Chama Furiosa",
        "type": "fogo",
        "power": 35,
        "challenge_type": CHALLENGE_MATH,
        "description": "Chamas intensas! Resolva a equação!",
    },
    "explosao_vulcanica": {
        "name": "Explosão Vulcânica",
        "type": "fogo",
        "power": 50,
        "challenge_type": CHALLENGE_EQUATION,
        "description": "O ataque supremo do fogo! Resolva a equação complexa!",
    },

    # ─── WATER MOVES ────────────────────────────────────────────────
    "jato_dagua": {
        "name": "Jato d'Água",
        "type": "agua",
        "power": 25,
        "challenge_type": CHALLENGE_MATH,
        "description": "Dispara um jato de água! Faça a conta!",
    },
    "bolha": {
        "name": "Bolha",
        "type": "agua",
        "power": 15,
        "challenge_type": CHALLENGE_MEMORY,
        "description": "Bolhas mágicas! Memorize o padrão!",
    },
    "defesa_aquatica": {
        "name": "Defesa Aquática",
        "type": "agua",
        "power": 10,
        "challenge_type": CHALLENGE_LOGIC,
        "description": "Escudo de água! Descubra a lógica!",
    },
    "mordida_gelada": {
        "name": "Mordida Gelada",
        "type": "agua",
        "power": 30,
        "challenge_type": CHALLENGE_MATH,
        "description": "Uma mordida congelante! Resolva rápido!",
    },
    "onda_poderosa": {
        "name": "Onda Poderosa",
        "type": "agua",
        "power": 35,
        "challenge_type": CHALLENGE_EQUATION,
        "description": "Uma onda gigante! Resolva a equação!",
    },
    "tsunami": {
        "name": "Tsunami",
        "type": "agua",
        "power": 50,
        "challenge_type": CHALLENGE_EQUATION,
        "description": "O poder dos mares! Equação complexa!",
    },

    # ─── PLANT MOVES ────────────────────────────────────────────────
    "folha_afiada": {
        "name": "Folha Afiada",
        "type": "planta",
        "power": 25,
        "challenge_type": CHALLENGE_MATH,
        "description": "Folhas cortantes! Resolva a conta!",
    },
    "absorver": {
        "name": "Absorver",
        "type": "planta",
        "power": 15,
        "challenge_type": CHALLENGE_MEMORY,
        "description": "Absorve energia! Memorize as cores!",
    },
    "espinhos": {
        "name": "Espinhos",
        "type": "planta",
        "power": 20,
        "challenge_type": CHALLENGE_LOGIC,
        "description": "Espinhos afiados! Ache o padrão!",
    },
    "chicote_de_vinha": {
        "name": "Chicote de Vinha",
        "type": "planta",
        "power": 35,
        "challenge_type": CHALLENGE_MATH,
        "description": "Chicote vegetal! Resolva a equação!",
    },
    "tempestade_de_petalas": {
        "name": "Tempestade de Pétalas",
        "type": "planta",
        "power": 50,
        "challenge_type": CHALLENGE_EQUATION,
        "description": "Pétalas mortais! Equação avançada!",
    },

    # ─── ELECTRIC MOVES ─────────────────────────────────────────────
    "choque": {
        "name": "Choque",
        "type": "eletrico",
        "power": 20,
        "challenge_type": CHALLENGE_MATH,
        "description": "Um choque elétrico! Conta rápida!",
    },
    "velocidade": {
        "name": "Velocidade",
        "type": "eletrico",
        "power": 15,
        "challenge_type": CHALLENGE_MEMORY,
        "description": "Velocidade máxima! Memorize rápido!",
    },
    "raio": {
        "name": "Raio",
        "type": "eletrico",
        "power": 30,
        "challenge_type": CHALLENGE_EQUATION,
        "description": "Um raio poderoso! Resolva a equação!",
    },
    "trovao": {
        "name": "Trovão",
        "type": "eletrico",
        "power": 40,
        "challenge_type": CHALLENGE_LOGIC,
        "description": "Trovão devastador! Lógica rápida!",
    },
    "tempestade_eletrica": {
        "name": "Tempestade Elétrica",
        "type": "eletrico",
        "power": 50,
        "challenge_type": CHALLENGE_EQUATION,
        "description": "O poder supremo! Equação complexa!",
    },

    # ─── NOVOS (GDD) ────────────────────────────────────────────────
    "erupcao_fatorial": {
        "name": "Erupção Fatorial",
        "type": "fogo",
        "power": 90,
        "challenge_type": CHALLENGE_MATH,
        "description": "Uma erupção escaldante! Matemática extrema!",
    },
    "mare_fracionada": {
        "name": "Maré Fracionada",
        "type": "agua",
        "power": 70,
        "challenge_type": CHALLENGE_MATH,
        "description": "Uma maré instável. Resolva com precisão!",
    },
    "raiz_quadrada": {
        "name": "Raiz Quadrada",
        "type": "planta",
        "power": 65,
        "challenge_type": CHALLENGE_EQUATION,
        "description": "Raízes profundas! Ache a incógnita da equação!",
    },
    "choque_de_sequencia": {
        "name": "Choque de Sequência",
        "type": "eletrico",
        "power": 60,
        "challenge_type": CHALLENGE_LOGIC,
        "description": "Choque padronizado! Lógica pura!",
    },
    "paradoxo": {
        "name": "Paradoxo",
        "type": "logico",
        "power": 80,
        "challenge_type": CHALLENGE_LOGIC,
        "description": "Um ataque que confunde! Lógica reversa!",
    },
    "cura_logica": {
        "name": "Cura Lógica",
        "type": "logico",
        "power": 0,
        "challenge_type": CHALLENGE_MEMORY,
        "description": "Recupera HP. Memorize para se curar!",
    },
}

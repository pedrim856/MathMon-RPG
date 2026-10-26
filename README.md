# MathMon RPG - Batalha de Raciocínio! 🧠⚔️

Um RPG educacional inspirado em clássicos como Pokémon Fire Red, onde a inteligência matemática e o raciocínio lógico são as principais armas para vencer as batalhas!

---

## 📖 Sobre o Jogo

**MathMon RPG** combina a mecânica nostálgica de exploração de mundos 2D em pixel art com desafios procedurais de matemática e lógica. Cada ataque desferido por seus monstrinhos depende da sua velocidade e exatidão ao resolver operações aritméticas, equações algébricas, desafios de lógica ou sequências de memória.

---

## 🎮 Controles

| Ação | Teclado Principal | Teclas Alternativas |
| :--- | :--- | :--- |
| **Mover Personagem** | `Setas Direcionais` | `W`, `A`, `S`, `D` |
| **Interagir / Confirmar / Atacar** | `Z` | `Enter` / `Espaço` |
| **Abrir Menu / Cancelar / Voltar** | `X` | `Escape` |
| **Opções de Resposta Rápida (1-4)** | `1`, `2`, `3`, `4` | Teclado Numérico (`KP1-KP4`) |
| **Digitação de Resposta Aberta** | `0` a `9`, `-`, `Backspace` | Digitação direta |

---

## 🌟 Principais Recursos

- **⚔️ Sistema de Batalha por Desafios**:
  - **Aritmética**: Adição, subtração, multiplicação e divisão com escalonamento de dificuldade.
  - **Equações**: Resolução rápida de equações lineares com incógnitas.
  - **Memória**: Retenção e repetição de sequências numéricas no tempo limite.
  - **Lógica**: Identificação de padrões, sequências lógicas e enigmas.
- **🐾 Variedade de Monstros**:
  - Elementos: Fogo, Água, Planta, Elétrico, Terra, Gelo, Lógico e Caos.
  - Atributos base de HP, Ataque, Defesa e Velocidade que influenciam na ordem dos turnos e cálculo de dano.
- **🗺️ Exploração & Overworld**:
  - Múltiplos mapas: *Vila Raiz*, *Floresta Enigma*, *Caverna Profunda* e *Arena Final*.
  - Encontros selvagens em grama alta e cavernas com taxa configurável.
  - NPCs com diálogos, treinadores desafiantes e sistema de evolução.
- **🎨 Interface Moderna**:
  - Efeitos de partículas e animações fluidas.
  - HUD informativo em tempo real com indicador de status da equipe e atalhos de controle.
  - Suporte completo a navegação por teclado e mouse.
- **💾 Sistema de Salvamento**:
  - Progresso persistido automaticamente em JSON com validação de integridade.

---

## 📂 Estrutura do Projeto

```text
MathMon-RPG/
├── battle/             # Mecânica e renderização do combate
│   ├── battle_engine.py    # Motor de turnos, dano e estado de batalha
│   └── battle_ui.py        # Interface visual, partículas e animações
├── data/               # Bases de dados do jogo
│   ├── items_db.py         # Itens utilizáveis e de mochila
│   ├── maps_data.py        # Configurações de tiles e layouts dos mapas
│   ├── monsters_db.py      # Atributos dos monstrinhos e encontros selvagens
│   ├── moves_db.py         # Golpes e multiplicadores de dano
│   └── questions_db.py     # Gerador procedural de problemas de raciocínio
├── entities/           # Entidades do jogo
│   ├── monster.py          # Classe de monstro, status e cálculo de atributos
│   ├── npc.py              # Personagens não-jogáveis e interações
│   └── player.py           # Personagem principal e detecção de movimento
├── states/             # Máquina de estados
│   ├── battle_state.py     # Controle de fluxo do combate e inputs
│   ├── evolution_state.py  # Tela de evolução de monstrinhos
│   ├── menu_state.py       # Menu principal e seleção de jogo
│   └── overworld_state.py  # Exploração do mundo aberto
├── ui/                 # Componentes gráficos de interface
│   ├── hud.py              # HUD do mundo aberto com status e dicas
│   ├── menu.py             # Menus modais, inventário e pausa
│   └── text_box.py         # Caixa de diálogos com efeito datilografia
├── utils/              # Módulos utilitários
│   ├── save_system.py      # Gerenciador de savegame em JSON
│   ├── sound.py            # Sintetizador procedural de áudio e efeitos sonoros
│   └── sprite_generator.py # Gerador de sprites procedurais em pixel art
├── world/              # Gerenciamento de mapas e visualização
│   ├── camera.py           # Câmera com interpolação suave
│   ├── maps.py             # Carregador de dados de cenários
│   └── tilemap.py          # Renderizador de matriz de tiles e colisões
├── game.py             # Núcleo da aplicação e loop principal do Pygame
├── main.py             # Ponto de entrada executável
├── settings.py         # Constantes de resolução, cores e balanceamento
└── requirements.txt    # Dependências do projeto
```

---

## 🚀 Como Executar

### Pré-requisitos
- **Python 3.10** ou superior instalado.

### 1. Clonar o repositório
```bash
git clone https://github.com/pedrim856/MathMon-RPG.git
cd MathMon-RPG
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Iniciar o jogo
```bash
python main.py
```

---

## 🧪 Executando Testes Automatizados

O projeto inclui suíte de testes unitários para validar geradores matemáticos e regras de batalha:

```bash
python -m unittest discover -s tests
```

---

## 📜 Licença

Desenvolvido para fins educacionais e de entretenimento por **MathMon Team**.
Distribuído sob a licença MIT.

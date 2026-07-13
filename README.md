# Project Genesis

Protótipo terminal de um simulador narrativo de gerenciamento de heróis.

## Rodar

```bash
python main.py
```

## MVP implementado

- Recrutar/criar personagens.
- Listar personagens com atributos, moral, lealdade, traços, medos, objetivos e memórias.
- Iniciar missão simples com estratégia cuidadosa, equilibrada ou agressiva.
- Resolver combate textual sem controle direto do jogador.
- Aplicar XP, ferimentos, morte permanente e memórias.
- Salvar/carregar o estado em `save/game_state.json`.

## Estrutura

- `entities/`: modelos centrais do jogo.
- `systems/`: regras de recrutamento, progressão, RNG e combate.
- `missions/`: geração de missões textuais.
- `simulation/`: execução do loop de missão.
- `ui/`: interface de terminal.
- `save/`: persistência JSON.
- `events/`: registro de acontecimentos.

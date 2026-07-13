from __future__ import annotations

import json
from pathlib import Path

from entities.game_state import GameState


DEFAULT_SAVE_PATH = Path(__file__).with_name("game_state.json")


def carregar_jogo(path: Path = DEFAULT_SAVE_PATH) -> GameState:
    if not path.exists():
        return GameState()

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return GameState.from_dict(data)


def salvar_jogo(state: GameState, path: Path = DEFAULT_SAVE_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(state.to_dict(), file, ensure_ascii=False, indent=2)
        file.write("\n")
    return path

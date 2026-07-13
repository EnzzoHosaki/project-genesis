from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import TypeVar

from entities.game_state import GameState


T = TypeVar("T")


class StateRng:
    """RNG deterministico e serializavel baseado em seed + contador."""

    def __init__(self, state: GameState):
        self.state = state

    def _next_raw(self) -> int:
        self.state.rng_passos += 1
        payload = f"{self.state.rng_seed}:{self.state.rng_passos}".encode("utf-8")
        digest = hashlib.sha256(payload).digest()
        return int.from_bytes(digest[:8], "big")

    def randint(self, minimo: int, maximo: int) -> int:
        if minimo > maximo:
            raise ValueError("minimo nao pode ser maior que maximo")
        return minimo + self._next_raw() % (maximo - minimo + 1)

    def choice(self, items: Sequence[T]) -> T:
        if not items:
            raise ValueError("nao e possivel escolher de uma sequencia vazia")
        return items[self.randint(0, len(items) - 1)]

    def sample(self, items: Sequence[T], quantidade: int) -> list[T]:
        if quantidade < 0:
            raise ValueError("quantidade nao pode ser negativa")
        quantidade = min(quantidade, len(items))
        pool = list(items)
        result = []
        for _ in range(quantidade):
            index = self.randint(0, len(pool) - 1)
            result.append(pool.pop(index))
        return result


def stable_choice(items: Sequence[T], key: str) -> T:
    if not items:
        raise ValueError("nao e possivel escolher de uma sequencia vazia")
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    index = int.from_bytes(digest[:8], "big") % len(items)
    return items[index]

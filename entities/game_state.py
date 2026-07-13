from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from entities.base import Base
from entities.hero import Hero
from events.game_event import GameEvent


@dataclass
class GameState:
    base: Base = field(default_factory=Base)
    herois: list[Hero] = field(default_factory=list)
    eventos: list[GameEvent] = field(default_factory=list)
    turno: int = 1
    rng_seed: int = 1729
    rng_passos: int = 0

    def herois_vivos(self) -> list[Hero]:
        return [hero for hero in self.herois if hero.vivo]

    def buscar_heroi(self, hero_id: str) -> Hero | None:
        for hero in self.herois:
            if hero.id == hero_id:
                return hero
        return None

    def registrar_evento(self, tipo: str, texto: str) -> None:
        self.eventos.append(GameEvent(self.turno, tipo, texto))
        if len(self.eventos) > 50:
            self.eventos = self.eventos[-50:]

    def to_dict(self) -> dict[str, Any]:
        return {
            "base": self.base.to_dict(),
            "herois": [hero.to_dict() for hero in self.herois],
            "eventos": [event.to_dict() for event in self.eventos],
            "turno": self.turno,
            "rng_seed": self.rng_seed,
            "rng_passos": self.rng_passos,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GameState:
        return cls(
            base=Base.from_dict(data.get("base", {})),
            herois=[Hero.from_dict(hero_data) for hero_data in data.get("herois", [])],
            eventos=[GameEvent.from_dict(event_data) for event_data in data.get("eventos", [])],
            turno=int(data.get("turno", 1)),
            rng_seed=int(data.get("rng_seed", 1729)),
            rng_passos=int(data.get("rng_passos", 0)),
        )

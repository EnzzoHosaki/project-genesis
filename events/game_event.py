from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GameEvent:
    turno: int
    tipo: str
    texto: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "turno": self.turno,
            "tipo": self.tipo,
            "texto": self.texto,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GameEvent:
        return cls(
            turno=int(data.get("turno", 0)),
            tipo=data.get("tipo", "evento"),
            texto=data.get("texto", ""),
        )

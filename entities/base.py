from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Base:
    nome: str = "Abrigo Genesis"
    instalacoes: dict[str, int] = field(
        default_factory=lambda: {
            "dormitorio": 1,
            "deposito": 1,
            "cozinha": 1,
        }
    )
    recursos: dict[str, int] = field(
        default_factory=lambda: {
            "suprimentos": 40,
            "creditos": 60,
            "medicamentos": 3,
        }
    )

    @property
    def capacidade_herois(self) -> int:
        return self.instalacoes.get("dormitorio", 0) * 4

    def to_dict(self) -> dict[str, Any]:
        return {
            "nome": self.nome,
            "instalacoes": self.instalacoes,
            "recursos": self.recursos,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Base:
        base = cls(nome=data.get("nome", "Abrigo Genesis"))
        base.instalacoes.update({key: int(value) for key, value in data.get("instalacoes", {}).items()})
        base.recursos.update({key: int(value) for key, value in data.get("recursos", {}).items()})
        return base

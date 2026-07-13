from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


ATTRIBUTES = ("forca", "agilidade", "mente", "vontade")


@dataclass
class Hero:
    id: str
    nome: str
    idade: int
    profissao: str
    classe: str
    atributos: dict[str, int]
    personalidade: str
    moral: int
    lealdade: int
    tracos: list[str]
    medos: list[str]
    objetivos: list[str]
    relacoes: dict[str, dict[str, int]] = field(default_factory=dict)
    memorias: list[str] = field(default_factory=list)
    xp: int = 0
    nivel: int = 1
    vivo: bool = True
    ferimentos: int = 0

    @property
    def poder(self) -> int:
        base = sum(self.atributos.get(attribute, 0) for attribute in ATTRIBUTES)
        return base + self.nivel * 2 - self.ferimentos

    def registrar_memoria(self, memoria: str) -> None:
        self.memorias.append(memoria)
        if len(self.memorias) > 20:
            self.memorias = self.memorias[-20:]

    def ganhar_xp(self, quantidade: int) -> list[str]:
        mensagens = []
        self.xp += quantidade
        while self.xp >= self.nivel * 100:
            self.xp -= self.nivel * 100
            self.nivel += 1
            menor_atributo = min(ATTRIBUTES, key=lambda atributo: self.atributos.get(atributo, 0))
            self.atributos[menor_atributo] = self.atributos.get(menor_atributo, 0) + 1
            self.moral = min(100, self.moral + 3)
            mensagens.append(f"{self.nome} subiu para o nivel {self.nivel}.")
        return mensagens

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "nome": self.nome,
            "idade": self.idade,
            "profissao": self.profissao,
            "classe": self.classe,
            "atributos": self.atributos,
            "personalidade": self.personalidade,
            "moral": self.moral,
            "lealdade": self.lealdade,
            "tracos": self.tracos,
            "medos": self.medos,
            "objetivos": self.objetivos,
            "relacoes": self.relacoes,
            "memorias": self.memorias,
            "xp": self.xp,
            "nivel": self.nivel,
            "vivo": self.vivo,
            "ferimentos": self.ferimentos,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Hero:
        return cls(
            id=data["id"],
            nome=data["nome"],
            idade=int(data["idade"]),
            profissao=data["profissao"],
            classe=data["classe"],
            atributos={key: int(value) for key, value in data["atributos"].items()},
            personalidade=data["personalidade"],
            moral=int(data["moral"]),
            lealdade=int(data["lealdade"]),
            tracos=list(data.get("tracos", [])),
            medos=list(data.get("medos", [])),
            objetivos=list(data.get("objetivos", [])),
            relacoes=dict(data.get("relacoes", {})),
            memorias=list(data.get("memorias", [])),
            xp=int(data.get("xp", 0)),
            nivel=int(data.get("nivel", 1)),
            vivo=bool(data.get("vivo", True)),
            ferimentos=int(data.get("ferimentos", 0)),
        )

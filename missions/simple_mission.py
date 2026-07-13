from __future__ import annotations

from dataclasses import dataclass

from entities.game_state import GameState
from systems.rng import StateRng, stable_choice


@dataclass(frozen=True)
class Mission:
    nome: str
    local: str
    objetivo: str
    ameaca: int
    inimigo: str
    recompensa_creditos: int
    recompensa_suprimentos: int

    @property
    def resumo(self) -> str:
        return (
            f"{self.nome} | Local: {self.local} | Objetivo: {self.objetivo} | "
            f"Ameaca: {self.ameaca}"
        )


NOMES = [
    "Sinal na Chuva",
    "Mapa Rasgado",
    "Fumaca no Horizonte",
    "Porta Sem Fechadura",
    "Vigilia Curta",
]

LOCAIS = [
    "mercado abandonado",
    "estacao de tratamento",
    "ponte velha",
    "bairro alagado",
    "torre de radio",
]

OBJETIVOS = [
    "recuperar suprimentos",
    "investigar pedido de socorro",
    "proteger uma rota",
    "mapear um abrigo vazio",
    "resgatar documentos",
]

INIMIGOS = [
    "saqueadores cansados, mas desesperados",
    "criaturas famintas atraidas por barulho",
    "um grupo armado defendendo territorio",
    "anomalias instaveis que distorcem a percepcao",
    "mercenarios sem bandeira",
]

COMPLICACOES = [
    "A estrada esta mais silenciosa do que deveria.",
    "Uma chuva fina apaga pegadas recentes.",
    "O radio chia com vozes que ninguem reconhece.",
    "Uma discussao interna atrasa a chegada.",
    "Marcas no chao sugerem que outra equipe passou por ali.",
]


def gerar_missao_simples(state: GameState) -> Mission:
    rng = StateRng(state)
    ameaca = 18 + state.turno * 2 + rng.randint(0, 8)
    return Mission(
        nome=rng.choice(NOMES),
        local=rng.choice(LOCAIS),
        objetivo=rng.choice(OBJETIVOS),
        ameaca=ameaca,
        inimigo=rng.choice(INIMIGOS),
        recompensa_creditos=15 + ameaca // 2,
        recompensa_suprimentos=8 + ameaca // 3,
    )


def gerar_complicacao(state: GameState, mission: Mission) -> str:
    key = f"{state.rng_seed}:{state.turno}:{mission.nome}:{mission.local}:{mission.objetivo}:complicacao"
    return stable_choice(COMPLICACOES, key)

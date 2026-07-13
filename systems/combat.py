from __future__ import annotations

from dataclasses import dataclass, field

from entities.game_state import GameState
from entities.hero import Hero
from systems.rng import StateRng, stable_choice


@dataclass
class CombatReport:
    textos: list[str] = field(default_factory=list)
    sobreviventes: list[Hero] = field(default_factory=list)
    mortos: list[Hero] = field(default_factory=list)
    vitoria: bool = False
    xp_base: int = 0


STRATEGY_ATTACK_MOD = {
    "cuidadosa": -2,
    "equilibrada": 0,
    "agressiva": 3,
}

STRATEGY_RISK_MOD = {
    "cuidadosa": -4,
    "equilibrada": 0,
    "agressiva": 5,
}


def resolver_combate(
    state: GameState,
    equipe: list[Hero],
    ameaca: int,
    inimigo: str,
    estrategia: str,
) -> CombatReport:
    rng = StateRng(state)
    report = CombatReport()
    vivos = [hero for hero in equipe if hero.vivo]
    estrategia = estrategia if estrategia in STRATEGY_ATTACK_MOD else "equilibrada"

    if not vivos:
        report.textos.append("Nao havia ninguem em condicoes de lutar.")
        return report

    report.textos.append(f"A equipe encontra {inimigo}. O confronto comeca sem ordens diretas.")
    total_equipe = 0
    contribuicoes: dict[str, int] = {}

    for hero in vivos:
        memoria_cautelosa = any("quase morreu" in memoria for memoria in hero.memorias)
        impulso_moral = (hero.moral - 50) // 10
        ajuste_memoria = -1 if memoria_cautelosa else 0
        rolagem = rng.randint(-3, 6)
        contribuicao = hero.poder + STRATEGY_ATTACK_MOD[estrategia] + impulso_moral + ajuste_memoria + rolagem
        contribuicoes[hero.id] = contribuicao
        total_equipe += contribuicao

        detalhe = _descrever_acao(state, hero, contribuicao)
        report.textos.append(detalhe)

    pressao_inimiga = ameaca + rng.randint(-4, 5)
    margem = total_equipe - pressao_inimiga
    report.vitoria = margem >= 0

    if report.vitoria:
        report.textos.append("A autonomia da equipe funciona: eles quebram o ritmo inimigo e vencem.")
        report.xp_base = 35 + max(0, ameaca // 2)
        _aplicar_consequencias_de_vitoria(state, vivos, margem, estrategia, report, rng)
    else:
        report.textos.append("A linha da equipe falha. A missao vira sobrevivencia.")
        report.xp_base = 15 + max(0, ameaca // 4)
        _aplicar_consequencias_de_derrota(state, vivos, abs(margem), estrategia, report, rng)

    report.sobreviventes = [hero for hero in equipe if hero.vivo]
    return report


def _descrever_acao(state: GameState, hero: Hero, contribuicao: int) -> str:
    if contribuicao >= hero.poder + 4:
        frases = [
            f"{hero.nome} assume risco antes que alguem peca e abre uma brecha.",
            f"{hero.nome} le o terreno com frieza e muda o ritmo da luta.",
            f"{hero.nome} protege um flanco que ninguem percebeu.",
        ]
    elif contribuicao >= hero.poder:
        frases = [
            f"{hero.nome} faz o necessario, sem brilho, mas sem hesitar.",
            f"{hero.nome} mantem a formacao viva por mais alguns segundos.",
            f"{hero.nome} responde bem a pressao.",
        ]
    else:
        frases = [
            f"{hero.nome} hesita quando uma memoria ruim pesa demais.",
            f"{hero.nome} perde espaco e precisa recuar.",
            f"{hero.nome} tenta ajudar, mas o medo interfere.",
        ]
    key = f"{state.rng_seed}:{state.turno}:{hero.id}:{contribuicao}:acao"
    return stable_choice(frases, key)


def _aplicar_consequencias_de_vitoria(
    state: GameState,
    vivos: list[Hero],
    margem: int,
    estrategia: str,
    report: CombatReport,
    rng: StateRng,
) -> None:
    risco_base = max(2, 12 - margem) + STRATEGY_RISK_MOD[estrategia]
    destaque = max(vivos, key=lambda hero: hero.poder + rng.randint(0, 3))
    destaque.registrar_memoria("virou um combate dificil")
    report.textos.append(f"{destaque.nome} sai da missao lembrado como decisivo.")

    for hero in vivos:
        risco = risco_base + hero.ferimentos * 2 - hero.moral // 25
        if any("quase morreu" in memoria for memoria in hero.memorias):
            risco -= 2
        if rng.randint(1, 20) <= risco:
            hero.ferimentos += 1
            hero.moral = max(0, hero.moral - 4)
            hero.registrar_memoria("quase morreu em uma vitoria apertada")
            report.textos.append(f"{hero.nome} sobrevive, mas ganha um ferimento serio.")
        else:
            hero.moral = min(100, hero.moral + 2)


def _aplicar_consequencias_de_derrota(
    state: GameState,
    vivos: list[Hero],
    margem_negativa: int,
    estrategia: str,
    report: CombatReport,
    rng: StateRng,
) -> None:
    risco_base = min(17, 6 + margem_negativa // 2) + STRATEGY_RISK_MOD[estrategia]
    candidatos = sorted(vivos, key=lambda hero: hero.poder + hero.moral // 10)

    for hero in candidatos:
        risco = risco_base + hero.ferimentos * 3 - hero.lealdade // 30
        risco = max(2, min(19, risco))
        salvador = _encontrar_salvador(hero, vivos, rng)
        if salvador is not None:
            risco -= 3
            salvador.moral = max(0, salvador.moral - 2)
            salvador.registrar_memoria(f"tentou salvar {hero.nome}")
            report.textos.append(f"{salvador.nome} ignora a propria seguranca para puxar {hero.nome} de volta.")

        if rng.randint(1, 20) <= risco:
            hero.vivo = False
            hero.moral = 0
            hero.registrar_memoria("morreu em missao")
            report.mortos.append(hero)
            report.textos.append(f"{hero.nome} nao retorna. A morte e permanente.")
            _marcar_luto(vivos, hero, report)
        else:
            hero.ferimentos += 1
            hero.moral = max(0, hero.moral - 8)
            hero.registrar_memoria("quase morreu em uma retirada caotica")
            report.textos.append(f"{hero.nome} escapa com ferimentos e uma nova memoria ruim.")


def _encontrar_salvador(alvo: Hero, equipe: list[Hero], rng: StateRng) -> Hero | None:
    candidatos = [hero for hero in equipe if hero.vivo and hero.id != alvo.id and hero.moral > 25]
    candidatos = rng.sample(candidatos, len(candidatos))
    for hero in candidatos:
        relacao = hero.relacoes.get(alvo.id, {})
        impulso = relacao.get("confianca", 0) + relacao.get("admiracao", 0) - relacao.get("tensao", 0)
        chance = hero.lealdade // 10 + impulso // 5
        if rng.randint(1, 20) <= chance:
            return hero
    return None


def _marcar_luto(equipe: list[Hero], morto: Hero, report: CombatReport) -> None:
    for hero in equipe:
        if hero.vivo and hero.id != morto.id:
            hero.moral = max(0, hero.moral - 10)
            hero.registrar_memoria(f"perdeu {morto.nome} em missao")
            relacao = hero.relacoes.setdefault(morto.id, {})
            relacao["confianca"] = max(0, relacao.get("confianca", 0) - 5)
    report.textos.append(f"A perda de {morto.nome} pesa na moral dos sobreviventes.")

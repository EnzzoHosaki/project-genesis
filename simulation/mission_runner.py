from __future__ import annotations

from dataclasses import dataclass, field

from entities.game_state import GameState
from entities.hero import Hero
from missions.simple_mission import Mission, gerar_complicacao, gerar_missao_simples
from systems.combat import resolver_combate
from systems.progression import conceder_xp


@dataclass
class MissionReport:
    mission: Mission
    textos: list[str] = field(default_factory=list)
    mortos: list[Hero] = field(default_factory=list)
    sucesso: bool = False


def iniciar_missao_simples(
    state: GameState,
    hero_ids: list[str],
    estrategia: str,
) -> MissionReport:
    mission = gerar_missao_simples(state)
    equipe = [hero for hero_id in hero_ids if (hero := state.buscar_heroi(hero_id)) and hero.vivo]
    report = MissionReport(mission=mission)

    if not equipe:
        report.textos.append("A missao foi cancelada: nao ha herois vivos na equipe.")
        return report

    custo_suprimentos = max(1, len(equipe) * 2)
    suprimentos = state.base.recursos.get("suprimentos", 0)
    if suprimentos < custo_suprimentos:
        report.textos.append("A missao foi cancelada: faltam suprimentos para preparar a equipe.")
        return report

    state.base.recursos["suprimentos"] = suprimentos - custo_suprimentos
    report.textos.append(f"Missao iniciada: {mission.nome}.")
    report.textos.append(f"Objetivo: {mission.objetivo} em {mission.local}.")
    report.textos.append(f"Estrategia definida: {estrategia}.")
    report.textos.append(gerar_complicacao(state, mission))

    combat_report = resolver_combate(
        state=state,
        equipe=equipe,
        ameaca=mission.ameaca,
        inimigo=mission.inimigo,
        estrategia=estrategia,
    )
    report.textos.extend(combat_report.textos)
    report.mortos = combat_report.mortos
    report.sucesso = combat_report.vitoria

    sobreviventes = [hero for hero in equipe if hero.vivo]
    if sobreviventes:
        report.textos.extend(conceder_xp(sobreviventes, combat_report.xp_base))

    if combat_report.vitoria:
        state.base.recursos["creditos"] = state.base.recursos.get("creditos", 0) + mission.recompensa_creditos
        state.base.recursos["suprimentos"] = (
            state.base.recursos.get("suprimentos", 0) + mission.recompensa_suprimentos
        )
        report.textos.append(
            f"A equipe retorna com {mission.recompensa_creditos} creditos e "
            f"{mission.recompensa_suprimentos} suprimentos."
        )
        for hero in sobreviventes:
            hero.registrar_memoria(f"concluiu {mission.nome}")
    else:
        report.textos.append("A equipe retorna quebrada, sem recompensa.")
        for hero in sobreviventes:
            hero.registrar_memoria(f"sobreviveu ao fracasso de {mission.nome}")

    state.registrar_evento(
        "missao",
        f"{mission.nome}: {'sucesso' if report.sucesso else 'fracasso'} com {len(report.mortos)} morte(s).",
    )
    state.turno += 1
    return report

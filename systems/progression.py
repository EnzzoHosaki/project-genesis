from __future__ import annotations

from entities.hero import Hero


def conceder_xp(heroes: list[Hero], quantidade: int) -> list[str]:
    mensagens = []
    for hero in heroes:
        if not hero.vivo:
            continue
        mensagens.append(f"{hero.nome} ganhou {quantidade} XP.")
        mensagens.extend(hero.ganhar_xp(quantidade))
    return mensagens

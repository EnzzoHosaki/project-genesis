from __future__ import annotations

from entities.game_state import GameState
from entities.hero import ATTRIBUTES, Hero
from systems.rng import StateRng


NOMES = [
    "Ari",
    "Bela",
    "Ciro",
    "Dara",
    "Eron",
    "Lina",
    "Mara",
    "Nilo",
    "Ravi",
    "Sana",
    "Tales",
    "Vera",
]

SOBRENOMES = [
    "Vale",
    "Rios",
    "Norte",
    "Cinza",
    "Moura",
    "Ferro",
    "Sol",
    "Lume",
    "Serra",
    "Vento",
]

PROFISSOES = [
    "cozinheiro de caravana",
    "vigia de armazem",
    "medica rural",
    "mensageira",
    "mecanico",
    "professora",
    "ex-guarda",
    "catador de ruinas",
    "cartografa",
    "artista de rua",
]

CLASSES = {
    "Vanguarda": {"forca": 2, "vontade": 1},
    "Batedor": {"agilidade": 2, "mente": 1},
    "Catalista": {"mente": 2, "vontade": 1},
    "Sentinela": {"vontade": 2, "forca": 1},
    "Mediador": {"mente": 1, "vontade": 1, "agilidade": 1},
}

PERSONALIDADES = [
    "calmo sob pressao",
    "impulsivo e protetor",
    "desconfiado",
    "curioso ate demais",
    "disciplinado",
    "gentil com estranhos",
    "ambicioso",
    "melancolico",
]

TRACOS = [
    "observador",
    "teimoso",
    "corajoso",
    "prudente",
    "sarcastico",
    "altruista",
    "orgulhoso",
    "paciente",
    "adaptavel",
    "reservado",
]

MEDOS = [
    "falhar com a equipe",
    "lugares fechados",
    "ficar para tras",
    "perder o controle",
    "ser esquecido",
    "fogo",
    "silencio absoluto",
    "multidoes em panico",
]

OBJETIVOS = [
    "encontrar alguem desaparecido",
    "provar que ainda e util",
    "juntar recursos para a familia",
    "fundar um refugio seguro",
    "aprender a liderar",
    "pagar uma divida antiga",
    "entender a origem das anomalias",
    "nunca mais fugir de uma crise",
]


def criar_heroi(state: GameState) -> Hero:
    rng = StateRng(state)
    nome = f"{rng.choice(NOMES)} {rng.choice(SOBRENOMES)}"
    classe = rng.choice(list(CLASSES))
    atributos = {attribute: rng.randint(2, 6) for attribute in ATTRIBUTES}
    for attribute, bonus in CLASSES[classe].items():
        atributos[attribute] += bonus

    hero = Hero(
        id=f"h-{state.turno}-{state.rng_passos}-{rng.randint(1000, 9999)}",
        nome=nome,
        idade=rng.randint(18, 52),
        profissao=rng.choice(PROFISSOES),
        classe=classe,
        atributos=atributos,
        personalidade=rng.choice(PERSONALIDADES),
        moral=rng.randint(45, 75),
        lealdade=rng.randint(35, 70),
        tracos=rng.sample(TRACOS, 2),
        medos=rng.sample(MEDOS, 1),
        objetivos=rng.sample(OBJETIVOS, 1),
    )
    hero.registrar_memoria(f"chegou ao {state.base.nome} no turno {state.turno}")
    return hero


def recrutar_heroi(state: GameState) -> tuple[Hero | None, str]:
    vivos = len(state.herois_vivos())
    if vivos >= state.base.capacidade_herois:
        return None, "O dormitorio esta lotado. Ninguem novo pode ficar na base agora."

    custo_creditos = 15
    custo_suprimentos = 4
    recursos = state.base.recursos
    if recursos.get("creditos", 0) < custo_creditos or recursos.get("suprimentos", 0) < custo_suprimentos:
        return None, "Faltam recursos para receber um novo recruta com seguranca."

    recursos["creditos"] -= custo_creditos
    recursos["suprimentos"] -= custo_suprimentos

    hero = criar_heroi(state)
    rng = StateRng(state)
    for existing in state.herois_vivos():
        confianca = rng.randint(0, 20)
        hero.relacoes[existing.id] = {
            "confianca": confianca,
            "admiracao": rng.randint(0, 15),
            "tensao": rng.randint(0, 10),
        }
        existing.relacoes[hero.id] = {
            "confianca": confianca,
            "admiracao": rng.randint(0, 15),
            "tensao": rng.randint(0, 10),
        }

    state.herois.append(hero)
    mensagem = (
        f"{hero.nome}, {hero.profissao}, aceitou ficar no {state.base.nome}. "
        f"Classe: {hero.classe}."
    )
    state.registrar_evento("recrutamento", mensagem)
    return hero, mensagem

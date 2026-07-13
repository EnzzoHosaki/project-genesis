from __future__ import annotations

from collections.abc import Callable

from entities.game_state import GameState
from entities.hero import ATTRIBUTES, Hero
from save.json_store import carregar_jogo, salvar_jogo
from simulation.mission_runner import iniciar_missao_simples
from systems.hero_factory import recrutar_heroi


class TerminalApp:
    def __init__(self) -> None:
        self.state = carregar_jogo()
        self.running = True
        self.actions: dict[str, Callable[[], None]] = {
            "1": self.mostrar_base,
            "2": self.recrutar,
            "3": self.listar_herois,
            "4": self.iniciar_missao,
            "5": self.mostrar_eventos,
            "6": self.salvar,
            "0": self.sair,
        }

    def run(self) -> None:
        self._print_header()
        while self.running:
            self._print_menu()
            escolha = input("> ").strip()
            action = self.actions.get(escolha)
            if action is None:
                print("Opcao invalida.")
                continue
            action()

    def _print_header(self) -> None:
        print("=" * 62)
        print("PROJECT GENESIS - MVP TERMINAL")
        print("Simulador narrativo de gerenciamento de herois")
        print("=" * 62)

    def _print_menu(self) -> None:
        print()
        print(f"Turno {self.state.turno} | Base: {self.state.base.nome}")
        print("1. Ver base")
        print("2. Recrutar personagem")
        print("3. Listar personagens")
        print("4. Iniciar missao simples")
        print("5. Ver eventos recentes")
        print("6. Salvar jogo")
        print("0. Sair")

    def mostrar_base(self) -> None:
        base = self.state.base
        print()
        print(f"Base: {base.nome}")
        print(f"Capacidade: {len(self.state.herois_vivos())}/{base.capacidade_herois} herois vivos")
        print("Instalacoes:")
        for nome, nivel in base.instalacoes.items():
            print(f"  - {nome}: nivel {nivel}")
        print("Recursos:")
        for nome, quantidade in base.recursos.items():
            print(f"  - {nome}: {quantidade}")

    def recrutar(self) -> None:
        hero, mensagem = recrutar_heroi(self.state)
        print()
        print(mensagem)
        if hero is not None:
            self._print_hero_card(hero)

    def listar_herois(self) -> None:
        print()
        if not self.state.herois:
            print("Nenhum personagem foi recrutado ainda.")
            return

        for index, hero in enumerate(self.state.herois, start=1):
            status = "vivo" if hero.vivo else "morto"
            print(f"{index}. {hero.nome} [{status}] - {hero.classe}, nivel {hero.nivel}, XP {hero.xp}")
            self._print_hero_card(hero, indent="   ")

    def iniciar_missao(self) -> None:
        vivos = self.state.herois_vivos()
        if not vivos:
            print()
            print("Nao ha herois vivos para enviar.")
            return

        print()
        print("Escolha a equipe por numero, separado por virgula. Exemplo: 1,2")
        for index, hero in enumerate(vivos, start=1):
            print(f"{index}. {hero.nome} - {hero.classe} | poder {hero.poder} | moral {hero.moral}")

        selecionados = self._ler_indices(len(vivos))
        if not selecionados:
            print("Missao cancelada.")
            return

        estrategia = self._escolher_estrategia()
        hero_ids = [vivos[index - 1].id for index in selecionados]
        report = iniciar_missao_simples(self.state, hero_ids, estrategia)

        print()
        print("-" * 62)
        print(report.mission.resumo)
        print("-" * 62)
        for texto in report.textos:
            print(texto)
        print("-" * 62)
        if report.mortos:
            nomes = ", ".join(hero.nome for hero in report.mortos)
            print(f"Mortos: {nomes}")
        print("Resultado:", "sucesso" if report.sucesso else "fracasso")

    def mostrar_eventos(self) -> None:
        print()
        if not self.state.eventos:
            print("Ainda nao ha eventos registrados.")
            return
        for event in self.state.eventos[-10:]:
            print(f"Turno {event.turno} [{event.tipo}] {event.texto}")

    def salvar(self) -> None:
        path = salvar_jogo(self.state)
        print()
        print(f"Jogo salvo em: {path}")

    def sair(self) -> None:
        print()
        escolha = input("Salvar antes de sair? [s/N] ").strip().lower()
        if escolha == "s":
            self.salvar()
        self.running = False
        print("A base fica em silencio. Ate a proxima.")

    def _ler_indices(self, maximo: int) -> list[int]:
        raw = input("> ").strip()
        if not raw:
            return []
        indices: list[int] = []
        for parte in raw.split(","):
            try:
                index = int(parte.strip())
            except ValueError:
                print(f"Entrada ignorada: {parte!r}")
                continue
            if 1 <= index <= maximo and index not in indices:
                indices.append(index)
            else:
                print(f"Indice fora do intervalo ou repetido: {index}")
        return indices

    def _escolher_estrategia(self) -> str:
        estrategias = {
            "1": "cuidadosa",
            "2": "equilibrada",
            "3": "agressiva",
        }
        print()
        print("Estrategia:")
        print("1. Cuidadosa - menos risco, menos iniciativa")
        print("2. Equilibrada - sem modificadores")
        print("3. Agressiva - mais impacto, mais risco")
        escolha = input("> ").strip()
        return estrategias.get(escolha, "equilibrada")

    def _print_hero_card(self, hero: Hero, indent: str = "") -> None:
        atributos = ", ".join(f"{name} {hero.atributos.get(name, 0)}" for name in ATTRIBUTES)
        memorias = "; ".join(hero.memorias[-3:]) if hero.memorias else "nenhuma"
        tracos = ", ".join(hero.tracos)
        medos = ", ".join(hero.medos)
        objetivos = ", ".join(hero.objetivos)
        print(f"{indent}Idade: {hero.idade} | Profissao: {hero.profissao}")
        print(f"{indent}Personalidade: {hero.personalidade}")
        print(f"{indent}Atributos: {atributos}")
        print(f"{indent}Moral {hero.moral} | Lealdade {hero.lealdade} | Ferimentos {hero.ferimentos}")
        print(f"{indent}Tracos: {tracos}")
        print(f"{indent}Medos: {medos}")
        print(f"{indent}Objetivo: {objetivos}")
        print(f"{indent}Memorias: {memorias}")

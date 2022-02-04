from aiogram.dispatcher.filters import Command as CommandFilter
from aiogram import Bot
from aiogramscenario import Machine, BaseScenario, Registrar
from dataclasses import dataclass

from .handlers import *
from .scenes import *
# from .scenes import Scenario, get_scenario


@dataclass
class Scenario(BaseScenario):  # сценарий-контейнер для сцен
    initial: InitialScene
    a: AScene
    b: BScene
    c: CScene


def get_scenario(bot: Bot) -> Scenario:
    return Scenario(
        initial=InitialScene(bot),
        a=AScene(bot),
        b=BScene(bot),
        c=CScene(bot)
    )


def setup_transitions(machine: Machine, scenario: BaseScenario) -> None:
    machine.add_transition(scenario.initial, scenario.a, process_start_command)  # /start InitialScene -> AScene
    for source_scene, destination_scene in ((scenario.initial, scenario.a),  # /next InitialScene -> BScene
                                            (scenario.a, scenario.b),  # /next AScene -> BScene
                                            (scenario.b, scenario.c)):  # /next BScene -> CScene
        machine.add_transition(source_scene, destination_scene, process_next_command)

def setup_handlers(registrar: Registrar, scenario: BaseScenario) -> None:
    # /start работает только на начальной сцене (InitialScene)
    registrar.register_message_handler(
        process_start_command,
        CommandFilter("start"),
        scene=scenario.initial
    )

    for scene in scenario:
        registrar.register_message_handler(
            process_restart_command,
            CommandFilter("restart"),
            scene=scene
        )
    # /next работает на всех сценах, кроме последней (CScene)
    for scene in scenario.select(exclude={scenario.c}):
        registrar.register_message_handler(
            process_next_command,
            CommandFilter("next"),
            scene=scene
        )

    # /back работает на всех сценах, кроме начальной (InitialScene)
    for scene in scenario.select(exclude={scenario.initial}):
        registrar.register_message_handler(
            process_back_command,
            CommandFilter("back"),
            scene=scene
        )

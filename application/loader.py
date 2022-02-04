from aiogram import Bot, Dispatcher
from aiogramscenario import Machine, MemorySceneStorage, Registrar, ScenarioMiddleware

from .configs import bot_token
from .scenes import setup_transitions, setup_handlers, get_scenario


def setup_middlewares(dispatcher: Dispatcher, machine: Machine) -> None:
    dispatcher.setup_middleware(ScenarioMiddleware(machine))

bot = Bot(bot_token)
dispatcher = Dispatcher(bot)

scenario = get_scenario(bot)  # сценарий-контейнер для сцен
scene_storage = MemorySceneStorage()
machine = Machine(scenario.initial, scene_storage=scene_storage)  # FSM
registrar = Registrar(dispatcher, machine)  # регистратор обработчиков


setup_transitions(machine, scenario)  # установка переходов
setup_middlewares(dispatcher, machine)  # установка слоёв промежуточной обработки
setup_handlers(registrar, scenario)  # установка обработчиков

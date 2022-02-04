import asyncio
import contextlib
from dataclasses import dataclass
from typing import Optional

from aiohttp import ClientSession
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.filters import Command as CommandFilter
from aiogramscenario import (Machine, ContextMachine, Registrar,
                             BaseScenario, ScenarioMiddleware, MemorySceneStorage)
import aiogramscenario


BOT_TOKEN = "..."

ENTER_TEXT = """Вы вошли в сцену «{scene_name}».

/next - перейти на следующую сцену.
/back - вернуться к предыдущей."""

EXIT_TEXT = """Вы вышли со сцены «{scene_name}».

/next - перейти на следующую сцену.
/back - вернуться к предыдущей."""


# собственная базовая сцена для своего подхода к инициализации, например, для DI
class BaseScene(aiogramscenario.BaseScene):

    def __init__(self, bot: Bot, name: Optional[str] = None):
        super().__init__(name=name)
        self._bot = bot

    async def process_enter(self, event: Message, data) -> None:
        text = ENTER_TEXT.format(scene_name=self.name)
        await self._bot.send_message(chat_id=event.chat.id, text=text)

    async def process_exit(self, event: Message, data) -> None:
        text = EXIT_TEXT.format(scene_name=self.name)
        await self._bot.send_message(chat_id=event.chat.id, text=text)


class InitialScene(BaseScene):
    pass


class AScene(BaseScene):
    pass


class BScene(BaseScene):
    pass


class CScene(BaseScene):
    pass


@dataclass
class Scenario(BaseScenario):  # сценарий-контейнер для сцен
    initial: InitialScene
    a: AScene
    b: BScene
    c: CScene


async def process_start_command(event: Message, machine: ContextMachine) -> None:
    bot = Bot.get_current()
    await bot.send_message(chat_id=event.chat.id, text="Приветствую вас!",
                           reply_to_message_id=event.message_id)
    await machine.execute_next_transition()


async def process_next_command(event: Message, machine: ContextMachine) -> None:
    bot = Bot.get_current()
    await bot.send_message(chat_id=event.chat.id, text="Идём вперёд...",
                           reply_to_message_id=event.message_id)
    await machine.execute_next_transition()


async def process_back_command(event: Message, machine: ContextMachine) -> None:
    bot = Bot.get_current()
    await bot.send_message(chat_id=event.chat.id, text="Идём назад...",
                           reply_to_message_id=event.message_id)
    await machine.execute_back_transition()


async def get_bot(token: str, session: ClientSession) -> Bot:
    bot = Bot(token)
    setattr(bot, "_session", session)  # для управления циклом жизни клиентской сессии

    return bot


def get_scenario(bot: Bot) -> Scenario:
    return Scenario(
        initial=InitialScene(bot),
        a=AScene(bot),
        b=BScene(bot),
        c=CScene(bot)
    )


def setup_handlers(registrar: Registrar, scenario: Scenario) -> None:
    # /start работает только на начальной сцене (InitialScene)
    registrar.register_message_handler(
        process_start_command,
        CommandFilter("start"),
        scene=scenario.initial
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


def setup_middlewares(dispatcher: Dispatcher, machine: Machine) -> None:
    dispatcher.setup_middleware(ScenarioMiddleware(machine))


def setup_transitions(machine: Machine, scenario: Scenario) -> None:
    machine.add_transition(scenario.initial, scenario.a, process_start_command)  # /start InitialScene -> AScene
    for source_scene, destination_scene in ((scenario.initial, scenario.a),  # /next InitialScene -> BScene
                                            (scenario.a, scenario.b),  # /next AScene -> BScene
                                            (scenario.b, scenario.c)):  # /next BScene -> CScene
        machine.add_transition(source_scene, destination_scene, process_next_command)


async def main():
    async with ClientSession() as session:
        bot = await get_bot(BOT_TOKEN, session)
        dispatcher = Dispatcher(bot)

        scenario = get_scenario(bot)  # сценарий-контейнер для сцен
        machine = Machine(scenario.initial, scene_storage=MemorySceneStorage())  # FSM
        registrar = Registrar(dispatcher, machine)  # регистратор обработчиков

        setup_transitions(machine, scenario)  # установка переходов
        setup_middlewares(dispatcher, machine)  # установка слоёв промежуточной обработки
        setup_handlers(registrar, scenario)  # установка обработчиков

        print("Start!")
        await dispatcher.start_polling(fast=False)


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):  # подавление трейсбека с KeyboardInterrupt
       asyncio.run(main())

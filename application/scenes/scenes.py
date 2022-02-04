from aiogram import Bot
from aiogram.types import Message
from typing import Optional

from aiogramscenario import BaseScenario, BaseScene

ENTER_TEXT = """Вы вошли в сцену «{scene_name}».

/next - перейти на следующую сцену.
/back - вернуться к предыдущей."""

EXIT_TEXT = """Вы вышли со сцены «{scene_name}».

/next - перейти на следующую сцену.
/back - вернуться к предыдущей."""


class Scene(BaseScene):

    def __init__(self, bot: Bot, name: Optional[str] = None):
        super().__init__(name=name)
        self._bot = bot

    async def process_enter(self, event: Message, data) -> None:
        text = ENTER_TEXT.format(scene_name=self.name)
        await self._bot.send_message(chat_id=event.chat.id, text=text)

    async def process_exit(self, event: Message, data) -> None:
        text = EXIT_TEXT.format(scene_name=self.name)
        await self._bot.send_message(chat_id=event.chat.id, text=text)


class InitialScene(Scene):
    pass


class AScene(Scene):
    pass


class BScene(Scene):
    pass


class CScene(Scene):
    pass

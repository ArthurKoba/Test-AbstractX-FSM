from aiogram.types import Message
from aiogramscenario import ContextMachine
from aiogram import Bot
from aiogram.types import Message


async def process_start_command(event: Message, machine: ContextMachine) -> None:
    bot = Bot.get_current()
    await bot.send_message(chat_id=event.chat.id, text="Приветствую вас!",
                           reply_to_message_id=event.message_id)
    await machine.execute_next_transition()

async def process_restart_command(event: Message, machine: ContextMachine) -> None:
    bot = Bot.get_current()
    await bot.send_message(chat_id=event.chat.id, text="Перезапуск системы!",
                           reply_to_message_id=event.message_id)
    await machine._machine.set_current_scene(
        scene=machine._machine.initial_scene,
        event=event,
        chat_id=event.chat.id,
        user_id=event.from_user.id,
    )


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

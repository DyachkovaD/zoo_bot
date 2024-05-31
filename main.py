import asyncio
import sys

import logging

from aiogram import F
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from aiogram.utils.keyboard import ReplyKeyboardBuilder

from token_data import TOKEN
from quiz_handler import router

dp = Dispatcher()
dp.include_router(router)

bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

class Quiz(StatesGroup):
    start_quiz = State()

@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    kb = [[types.KeyboardButton(text='Квиз!')]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
    await message.answer(f'Привет! \nДавайте узнаем Ваше тотемное животное!', reply_markup=keyboard)


# @dp.message(F.text.lower() == 'связаться с сотрудником')
# async def contact(message: types.Message):
#     await bot.send_message(chat_id=1875707606)


async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
   logging.basicConfig(level=logging.INFO, stream=sys.stdout)
   asyncio.run(main())

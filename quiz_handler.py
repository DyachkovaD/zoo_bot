import aiohttp

from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.formatting import (
    as_list, as_marked_section
)
from aiogram import F

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, types
from random import sample

from questions import QUESTIONS
from questions import ANIMALS

router = Router()

class Quiz(StatesGroup):
    quest = State()
    rezult_messsage = State()
    feadback = State()

quiz_rezult = {'amphibian': 0,
               'reptile': 0,
               'mammal': 0,
               'bird': 0}

questions = QUESTIONS.copy()

feadbacks = []

@router.message(F.text.lower() == 'квиз!')
async def quiz_start(message: types.Message, state: FSMContext):
    await state.set_state(Quiz.quest.state)
    kb = [[types.KeyboardButton(text='Начать')]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
    await message.answer(f'Начнём?', reply_markup=keyboard)


@router.message(Quiz.quest)
async def make_question(message: types.Message, state: FSMContext):
    if message.text.strip().lower() not in ['1', '2', '3', '4', 'начать']:
        await message.answer(f'Я Вас не понял \nОтветом могут быть только цифры от 1 до 4')
        return

    if not questions:
        await state.clear()
        win_category = max(quiz_rezult, key=quiz_rezult.get)
        for category, animals in ANIMALS.items():
            if category == win_category:
                win_animal = sample(animals, 1)[0]

                rezult_message = f'🫧 Вы можете стать опекуном этого милого создания и частью большого круга друзей Московского зоопарка\n' \
                                 f'🐾 Ваш возможный подопечный: <a href="{win_animal["url"]}">{win_animal["name"]}</a> 🐾 \n\n' \
                                 f'🫧 Подробнее о программе опекунства: ' \
                                 f'<a href="https://moscowzoo.ru/about/guardianship">«Клуб друзей зоопарка»</a>'

                await state.set_data({'rezult_message': rezult_message})

                kb = [[
                    InlineKeyboardButton(text='Попробовать ещё раз?', callbackdata='Попробовать ещё раз'),
                    InlineKeyboardButton(text='Связаться с сотрудником', callbackdata='Связаться с сотрудником'),
                    InlineKeyboardButton(text='Поделиться в VK', url=f'https://vk.com/share.php?title={rezult_message}\n@totem_zoo_bot'),
                    InlineKeyboardButton(text='Оставить отзыв', callback_data='Отзыв')
                ]]
                inlinekb = InlineKeyboardMarkup(inline_keyboard=kb)


                await message.answer(f'Вы завершили викторину \n'
                                     f'Ваше тотемное животное: {win_animal["name"]}')
                await message.answer_photo(photo=win_animal['photo'])

                await message.answer(rezult_message, parse_mode='HTML', reply_markup=inlinekb)


    if message.text in ['1', '2', '3', '4']:
        if message.text == '1':
            quiz_rezult['amphibian'] += 1
        elif message.text == '2':
            quiz_rezult['reptile'] += 1
        elif message.text == '3':
            quiz_rezult['mammal'] += 1
        elif message.text == '4':
            quiz_rezult['bird'] += 1

    question = sample(questions, 1)[0]
    questions.pop(questions.index(question))
    answers = question['answers']
    builder = ReplyKeyboardBuilder()
    num = ['1', '2', '3', '4']
    for _ in num:
        builder.add(types.KeyboardButton(text=_))
    builder.adjust(4)

    await message.answer(
        f"{question['question']} \n"
        f"1) {answers[0]}\n"
        f"2) {answers[1]}\n"
        f"3) {answers[2]}\n"
        f"4) {answers[3]}\n",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )

@router.message(F.text.lower() == 'попробовать ещё раз')
async def retry(message: types.Message, state: FSMContext):
    global quiz_rezult, questions
    quiz_rezult = {'amphibian': 0,
                   'reptile': 0,
                   'mammal': 0,
                   'bird': 0}

    questions = QUESTIONS.copy()

    await state.set_state(Quiz.quest.state)
    kb = [[types.KeyboardButton(text='Начать')]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
    await message.answer(f'Начнём?', reply_markup=keyboard)

@router.message(F.text.lower() == 'связаться с сотрудником')
async def contact(message: types.Message, state: FSMContext):
    global bot
    rezult_message = await state.get_data()
    await bot.send_message(chat_id=1875707606, text=rezult_message['rezult_message'])
    await message.answer(f'✏️telegram: @darya_dy99\n'
                         f'✉️e-mail: yki.yki@bk.ru\n'
                         f'📞   +7-9хх-ххх-хх-хх')

@router.message(F.text.lower() == 'отзыв')
async def feadback_state(message: types.Message, state: FSMContext):
    await state.set_state(Quiz.feadback.state)
    await message.answer(f'Напишите что Вы думаете о нашем боте или свои предложения для его улучшения. \n'
                         f'А мы постараемся сделать его удобнее для Вас 🐻‍❄')

@router.message(Quiz.feadback)
async def feadback_get(message: types.Message, state: FSMContext):
    feadbacks.append(
        {
            'feadback': message.text,
            'user': message.from_user.username
         }
    )
    await message.answer(f'Спасибо за Ваш отзыв! 🦉')
    await state.clear()
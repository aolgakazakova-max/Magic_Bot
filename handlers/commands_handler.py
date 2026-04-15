import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.inline import (
    main_menu,
    persons_keyboard,
    analysis_menu,
    topics_keyboard,
    gpt_keyboard,
    help_keyboard,
    translate_language_keyboard
)

from states.state import TalkStates, QuizStates, GptStates
from data.topics import TOPICS
from handlers.random_fact import send_random_fact
from handlers.talk import PERSONS

router = Router()
logger = logging.getLogger(__name__)


# =======================
# UTIL: TRANSLATE SCREEN
# =======================
async def open_translate(target):
    await target.answer(
        "🌍 Выберите язык перевода:",
        reply_markup=translate_language_keyboard()
    )


# =======================
# COMMANDS
# =======================

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        f"Привет, <b>{message.from_user.first_name or 'Пользователь'}!</b>",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )


@router.message(F.text == "/stop")
async def cmd_stop(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Бот остановлен. Нажми /start чтобы начать снова")


@router.message(F.text == "/help")
async def cmd_help(message: Message):
    await message.answer(
        "📌 Команды бота:\n\n"
        "/start — главное меню\n"
        "/help — инфо\n"
        "/stop — остановить текущий режим\n"
        "/gpt — ChatGPT\n"
        "/talk — диалог с личностью\n"
        "/quiz — квиз\n"
        "/translate — перевод\n"
        "/analytics — аналитика\n",
        reply_markup=help_keyboard()
    )


@router.message(F.text == "/gpt")
async def cmd_gpt(message: Message, state: FSMContext):
    await state.set_state(GptStates.chatting)
    await state.update_data(history=[])

    await message.answer(
        "🤖 GPT режим включен\nНапиши сообщение:",
        reply_markup=gpt_keyboard()
    )


@router.message(F.text == "/talk")
async def cmd_talk(message: Message, state: FSMContext):
    await state.set_state(TalkStates.choosing_person)

    await message.answer(
        "Выберите персонажа:",
        reply_markup=persons_keyboard(PERSONS)
    )


@router.message(F.text == "/quiz")
async def cmd_quiz(message: Message, state: FSMContext):
    await state.set_state(QuizStates.choosing_topic)

    await message.answer(
        "Выберите тему:",
        reply_markup=topics_keyboard(TOPICS)
    )


@router.message(F.text == "/analytics")
async def cmd_analytics(message: Message):
    await message.answer(
        "📊 Аналитика:",
        reply_markup=analysis_menu()
    )


@router.message(F.text == "/translate")
async def cmd_translate(message: Message):
    await open_translate(message)


# =======================
# CALLBACKS
# =======================

@router.callback_query(F.data == "menu:gpt")
async def cb_gpt(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GptStates.chatting)
    await state.update_data(history=[])

    await callback.message.answer("🤖 GPT режим включен", reply_markup=gpt_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu:random")
async def cb_random(callback: CallbackQuery):
    await send_random_fact(callback.message)
    await callback.answer()


@router.callback_query(F.data == "menu:talk")
async def cb_talk(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TalkStates.choosing_person)

    await callback.message.answer(
        "Выберите персонажа:",
        reply_markup=persons_keyboard(PERSONS)
    )
    await callback.answer()


@router.callback_query(F.data == "menu:quiz")
async def cb_quiz(callback: CallbackQuery, state: FSMContext):
    await state.set_state(QuizStates.choosing_topic)

    await callback.message.answer(
        "Выберите тему:",
        reply_markup=topics_keyboard(TOPICS)
    )
    await callback.answer()


@router.callback_query(F.data == "menu:analytics")
async def cb_analytics(callback: CallbackQuery):
    await callback.message.answer(
        "📊 Аналитика:",
        reply_markup=analysis_menu()
    )
    await callback.answer()


# =======================
# TRANSLATE (FIX)
# =======================

@router.callback_query(F.data == "menu:translate")
async def cb_translate(callback: CallbackQuery):
    await callback.answer()
    await open_translate(callback.message)


# =======================
# HELP MENU
# =======================

@router.callback_query(F.data == "menu:help")
async def cb_help(callback: CallbackQuery):
    await callback.message.answer(
        "📌 Команды бота:\n\n"
        "/start — главное меню\n"
        "/help — инфо\n"
        "/stop — остановить текущий режим\n"
        "/gpt — ChatGPT\n"
        "/talk — диалог с личностью\n"
        "/quiz — квиз\n"
        "/translate — перевод\n"
        "/analytics — аналитика\n",
        reply_markup=help_keyboard()
    )
    await callback.answer()


# =======================
# BACK BUTTON
# =======================

@router.callback_query(F.data == "menu:back")
async def cb_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.answer("🏠 Главное меню", reply_markup=main_menu())
    await callback.answer()
import logging
from pathlib import Path

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from handlers.talk import PERSONS
from keyboards.inline import main_menu, random_keyboard, gpt_keyboard, persons_keyboard, analysis_menu
from states.state import TalkStates, TranslateStates
from handlers.random_fact import send_random_fact

router = Router()
logger = logging.getLogger(__name__)

IMAGES_PATH = Path("images")



@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"Привет, <b>{message.from_user.first_name or 'Пользователь'}</b>!\n"
        "Выбери что тебя интересует:",
        reply_markup=main_menu(),
        parse_mode="html"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>Команды:</b>\n"
        "/start - Главное меню\n"
        "/random - Случайный факт\n"
        "/gpt - Диалог с ChatGPT\n"
        "/talk - Диалог с известной личностью\n"
        "/quiz - Квиз\n"
        "/translate - Переводчик\n"
        "/analytics - Аналитика",
        reply_markup=main_menu(),
        parse_mode="html"
    )



async def safe_send_photo(target, photo_path, caption):

    msg = target.message if isinstance(target, CallbackQuery) else target

    try:
        # Пытаемся отредактировать старое на новое фото (для чистоты чата)
        photo = FSInputFile(photo_path)
        await msg.edit_media(media=InputMediaPhoto(media=photo, caption=caption))
    except:
        # Если не получилось отредактировать (например, старое было текстом), просто шлем новое
        await msg.answer_photo(photo=FSInputFile(photo_path), caption=caption)



@router.callback_query(F.data == "menu:random")
async def menu_random(callback: CallbackQuery):
    await callback.answer()
    await safe_send_photo(callback, "random.png", "🎲 Случайный факт")
    await send_random_fact(callback.message, reply_markup=random_keyboard())


@router.callback_query(F.data == "menu:gpt")
async def menu_gpt(callback: CallbackQuery):
    await callback.answer()
    await safe_send_photo(callback, "gpt.png", "🤖 Режим ChatGPT\nНапиши /gpt чтобы начать")
    await callback.message.answer("Используй клавиатуру для выхода из режима:", reply_markup=gpt_keyboard())


@router.callback_query(F.data == "menu:talk")
async def menu_talk(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await state.set_state(TalkStates.choosing_person)
    await safe_send_photo(callback, "talk.png", "🗣️ Диалог с личностью\nВыбери собеседника:")

    await callback.message.answer(reply_markup=persons_keyboard(PERSONS))


@router.callback_query(F.data == "menu:quiz")
async def menu_quiz(callback: CallbackQuery):
    await callback.answer()
    await safe_send_photo(callback, "quiz.png", "🎯 Квиз из\nСкоро будет доступен")


@router.callback_query(F.data == "menu:translate")
async def menu_translate(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await state.set_state(TranslateStates.waiting_for_text)
    await safe_send_photo(callback, "translate.png", "🔃 Переводчик")
    await callback.message.answer("✏️ Отправь текст для перевода:")


@router.callback_query(F.data == "menu:analytics")
async def menu_analytics(callback: CallbackQuery):
    await callback.answer()
    await safe_send_photo(callback, "images/analytics.png", "📈 Аналитика\nВыбери действие:")
    await callback.message.answer(
        "📊 Выберите действие:",
        reply_markup=analysis_menu()
    )
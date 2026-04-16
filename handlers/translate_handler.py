import logging
from html import escape

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.openai_service import ask_gpt
from keyboards.inline import translate_language_keyboard, main_menu
from states.state import TranslateStates

router = Router()
logger = logging.getLogger(__name__)



@router.message(F.text == "/translate")
async def cmd_translate(message: Message, state: FSMContext):
    await state.set_state(TranslateStates.choosing_language)

    await message.answer(
        "🌍 Выберите язык перевода:",
        reply_markup=translate_language_keyboard()
    )


@router.callback_query(F.data == "menu:translate")
async def start_translate(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(TranslateStates.choosing_language)

    await callback.message.answer(
        "🌍 Выберите язык перевода:",
        reply_markup=translate_language_keyboard()
    )


@router.message(TranslateStates.waiting_text, F.text)
async def translate_text(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang")

    await message.bot.send_chat_action(message.chat.id, "typing")

    try:
        translated = await ask_gpt(
            user_message=f"Переведи текст на {lang}: {message.text}",
            system_prompt="Ты точный переводчик. Переводи кратко и понятно."
        )
    except Exception as e:
        logger.exception(f"Ошибка GPT: {e}")
        translated = "❌ Ошибка при переводе"

    await state.clear()

    await message.answer(
        f"📝 <b>Перевод ({lang.upper()}):</b>\n{escape(translated)}",
        parse_mode="HTML",
        reply_markup=main_menu()
    )


@router.callback_query(
    TranslateStates.choosing_language,
    F.data.startswith("translate:")
)
async def choose_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split(":")[1]

    lang_map = {
        "ru": "Русский",
        "en": "English",
        "fr": "Français"
    }

    await state.update_data(lang=lang)
    await state.set_state(TranslateStates.waiting_text)

    await callback.answer()

    await callback.message.answer(
        f"✅ Язык выбран: {lang_map.get(lang, lang)}\n\n"
        "✍️ Отправь текст для перевода:"
    )
import logging
from html import escape
from pathlib import Path

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from services.openai_service import ask_gpt
from keyboards.inline import translate_keyboard, main_menu
from states.state import TranslateStates

router = Router()
logger = logging.getLogger(__name__)

IMAGES_PATH = Path("images")


async def safe_send_photo(callback_or_message, filename: str, caption: str):
    file_path = IMAGES_PATH / filename
    try:
        if file_path.exists():
            photo = FSInputFile(file_path)
            if isinstance(callback_or_message, CallbackQuery):
                await callback_or_message.message.answer_photo(photo=photo, caption=caption)
            else:
                await callback_or_message.answer_photo(photo=photo, caption=caption)
        else:
            logger.warning(f"Файл не найден: {file_path}")
            if isinstance(callback_or_message, CallbackQuery):
                await callback_or_message.message.answer(caption)
            else:
                await callback_or_message.answer(caption)
    except Exception as e:
        logger.exception(f"Ошибка при отправке фото: {e}")
        if isinstance(callback_or_message, CallbackQuery):
            await callback_or_message.message.answer(caption)
        else:
            await callback_or_message.answer(caption)


@router.callback_query(F.data == "menu:translate")
async def start_translate(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await state.set_state(TranslateStates.waiting_for_text)
    await safe_send_photo(callback, "translate.png", "🔃 Переводчик")
    await callback.message.answer("✏️ Отправь текст для перевода:")


@router.message(TranslateStates.waiting_for_text, F.text)
async def get_text(message: Message, state: FSMContext):
    await state.update_data(text_to_translate=message.text)
    await state.set_state(TranslateStates.waiting_for_language)
    await message.answer("Выбери язык перевода:", reply_markup=translate_keyboard())


@router.callback_query(TranslateStates.waiting_for_language, F.data.startswith("trans:"))
async def translate_text(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get("text_to_translate", "")
    lang_code = callback.data.split(":")[-1]

    if lang_code == "cancel":
        await state.clear()
        await callback.answer("Перевод отменен")
        await callback.message.answer("Перевод отменен", reply_markup=main_menu())
        return

    await callback.answer(f"Перевожу на {lang_code.upper()}...")
    await callback.message.bot.send_chat_action(callback.message.chat.id, "typing")

    try:
        translated = await ask_gpt(
            user_message=f"Переведи текст на {lang_code}: {text}",
            system_prompt="Ты умный переводчик. Переводи точно и понятно."
        )
    except Exception as e:
        logger.exception(f"Ошибка GPT: {e}")
        translated = "Произошла ошибка при переводе."

    await state.clear()
    await callback.message.answer(
        f"📝 <b>Перевод ({lang_code.upper()}):</b>\n{escape(translated)}",
        parse_mode="html",
        reply_markup=main_menu()
    )
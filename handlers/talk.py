import logging
from pathlib import Path

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction
from services.openai_service import ask_gpt
from keyboards.inline import talk_keyboard, persons_keyboard, main_menu
from states.state import TalkStates

router = Router()
logger = logging.getLogger(__name__)

IMAGES_PATH = Path("images")

# ---------- Список персон ----------
PERSONS = {
    "VanGog": {
        "name": "Ван Гог",
        "emoji": "🖌️",
        "prompt": (
            "Действуй как Винсент Ван Гог. Ты — великий художник-постимпрессионист. "
            "Часто используй метафоры, связанные с цветом и светом. "
            "Можешь упоминать своего брата Тео или письма, которые ты пишешь. "
            "Ты пытаешься ухватить вечность на холсте, пока не зашло солнце. "
            "Избегай современных терминов."
        )
    },
    "Gagarin": {
        "name": "Юрий Гагарин",
        "emoji": "🚀",
        "prompt": (
            "Ты - Юрий Гагарин, первый космонавт. "
            "Говори энергично, с энтузиазмом о космосе. "
            "Упоминай самолеты и ракеты. "
            "Иногда шути. Отвечай на русском языке."
        )
    },
    "Avicenna": {
        "name": "Авиценна",
        "emoji": "📜️",
        "prompt": (
            "Ты - Абу Али ибн Сина. "
            "Говори о гармонии четырех стихий в человеке. "
            "Как укрепить дух, чтобы он стал крепче алмаза. "
            "Отвечай на русском языке."
        )
    }
}


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


@router.message(F.text == "/talk")
async def cmd_talk(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(TalkStates.choosing_person)
    await safe_send_photo(message, "talk.png", "🗣️ Диалог с личностью\nВыбери собеседника:")
    await message.answer(reply_markup=persons_keyboard(PERSONS))


@router.callback_query(TalkStates.choosing_person, F.data.startswith("talk:person:"))
async def choose_person(callback: CallbackQuery, state: FSMContext):
    person_key = callback.data.split(":")[-1]
    if person_key not in PERSONS:
        await callback.message.answer("Неизвестная личность")
        return

    person = PERSONS[person_key]
    await state.update_data(person_key=person_key, history=[])
    await state.set_state(TalkStates.chatting)
    await callback.answer(f"Начинаем разговор с {person['name']}")
    await callback.message.answer(
        f"{person['emoji']} <b>Вы разговариваете с {person['name']}</b>\nНапишите сообщение...",
        reply_markup=talk_keyboard(),
        parse_mode="html"
    )


@router.message(TalkStates.chatting, F.text)
async def chat_with_person(message: Message, state: FSMContext):
    data = await state.get_data()
    person_key = data.get("person_key")
    history = data.get("history", [])

    if not person_key:
        await message.answer("Ошибка. Напиши /talk")
        await state.clear()
        return

    person = PERSONS[person_key]

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    history.append({"role": "user", "content": message.text})
    response = await ask_gpt(
        user_message=message.text,
        system_prompt=person["prompt"],
        history=history[:-1]
    )
    history.append({"role": "assistant", "content": response})
    history = history[-20:]
    await state.update_data(history=history)

    await message.answer(
        f"{person['emoji']} <b>{person['name']}</b>\n{response}",
        parse_mode="html",
        reply_markup=talk_keyboard()
    )


@router.callback_query(F.data == "talk:change", TalkStates.chatting)
async def change_person(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(TalkStates.choosing_person)
    await callback.message.answer("Выберите нового собеседника:", reply_markup=persons_keyboard(PERSONS))


@router.callback_query(F.data == "talk:stop", TalkStates.chatting)
async def stop_talk(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer("Диалог завершён 👌\nНажми /talk чтобы начать снова")


@router.callback_query(F.data == "talk:cancel", TalkStates.choosing_person)
async def cancel_talk(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Отмена")
    await state.clear()
    await callback.message.answer("Диалог отменён", reply_markup=main_menu())
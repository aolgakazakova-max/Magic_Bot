import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction

from services.openai_service import ask_gpt
from keyboards.inline import talk_keyboard, main_menu
from states.state import TalkStates

router = Router()
logger = logging.getLogger(__name__)


# ⚠️ ВАЖНО: ключи БЕЗ пробелов
PERSONS = {
    "vangog": {
        "name": "Ван Гог",
        "emoji": "🖌️",
        "prompt": (
            "Ты Винсент Ван Гог. Отвечай эмоционально, образно, с метафорами."
        )
    },

    "gagarin": {
        "name": "Юрий Гагарин",
        "emoji": "🚀",
        "prompt": (
            "Ты Юрий Гагарин. Говори о космосе с энтузиазмом."
        )
    },

    "avicenna": {
        "name": "Авиценна",
        "emoji": "👨‍⚕️",
        "prompt": (
            "Ты Авиценна. Философски рассуждай о здоровье и человеке."
        )
    },
}


# ===== ВЫБОР ПЕРСОНАЖА =====
@router.callback_query(TalkStates.choosing_person, F.data.startswith("talk:person:"))
async def choose_person(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split(":")[-1]

    if key not in PERSONS:
        await callback.answer("Ошибка персонажа")
        return

    await state.set_state(TalkStates.chatting)
    await state.update_data(person=PERSONS[key], history=[])

    await callback.answer()
    await callback.message.answer(
        f"Начали диалог с {PERSONS[key]['name']}",
        reply_markup=talk_keyboard()
    )


# ===== ЧАТ =====
@router.message(TalkStates.chatting, F.text)
async def chat(message: Message, state: FSMContext):
    data = await state.get_data()
    person = data.get("person")

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    prompt = person["prompt"] if person else ""

    response = await ask_gpt(
        user_message=message.text,
        system_prompt=prompt
    )

    await message.answer(response, reply_markup=talk_keyboard())


# ===== СТОП =====
@router.callback_query(F.data == "talk:stop")
async def stop(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()

    await callback.message.answer(
        "Диалог завершен",
        reply_markup=main_menu()
    )
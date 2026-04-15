from html import escape

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction

from states.state import GptStates
from services.openai_service import ask_gpt
from keyboards.inline import gpt_keyboard, main_menu

router = Router()


# ===== GPT CHAT =====
@router.message(GptStates.chatting, F.text)
async def gpt_chat(message: Message, state: FSMContext):
    data = await state.get_data()
    history = data.get("history", [])

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    history.append({"role": "user", "content": message.text})

    try:
        response = await ask_gpt(
            user_message=message.text,
            history=history
        )
    except Exception:
        response = "Ошибка GPT"

    history.append({"role": "assistant", "content": response})
    history = history[-20:]

    await state.update_data(history=history)

    await message.answer(
        escape(response),
        reply_markup=gpt_keyboard(),
        parse_mode="HTML"
    )


# ===== STOP GPT =====
@router.callback_query(F.data == "gpt:stop")
async def stop_gpt(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()

    await callback.message.answer(
        "GPT остановлен",
        reply_markup=main_menu()
    )
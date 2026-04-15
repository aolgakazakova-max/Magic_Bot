import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatAction

from states.state import QuizStates
from keyboards.inline import topics_keyboard, after_answer_keyboard, main_menu
from utils.quiz_generate import send_next_question, check_answer
from data.topics import TOPICS

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(QuizStates.choosing_topic, F.data.startswith('quiz:topic:'))
async def on_topic(callback: CallbackQuery, state: FSMContext):
    topic_key = callback.data.split(":")[-1]

    await state.update_data(topic_key=topic_key, score=0, total=0)
    await state.set_state(QuizStates.answering)

    await callback.answer()

    await callback.message.answer("Генерирую вопрос...")
    await send_next_question(callback.message, state, topic_key)


@router.message(QuizStates.answering, F.text)
async def answer(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    is_correct, explanation = await check_answer(
        data["current_question"], message.text
    )

    score = data.get("score", 0) + int(is_correct)
    total = data.get("total", 0) + 1

    await state.update_data(score=score, total=total)

    await message.answer(
        f"{'✅' if is_correct else '❌'}\n{explanation}\n\nСчет: {score}/{total}",
        reply_markup=after_answer_keyboard()
    )


@router.callback_query(F.data == "quiz:next")
async def next_q(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    await send_next_question(callback.message, state, data["topic_key"])


@router.callback_query(F.data == "quiz:stop")
async def stop_q(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await state.clear()
    await callback.answer()

    await callback.message.answer(
        f"Итог: {data.get('score', 0)}/{data.get('total', 0)}",
        reply_markup=main_menu()
    )


@router.callback_query(F.data == "quiz:cancel")
async def cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()

    await callback.message.answer(
        "Квиз отменен",
        reply_markup=main_menu()
    )
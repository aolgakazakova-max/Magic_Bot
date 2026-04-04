import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction
from aiogram.types import Message, FSInputFile, CallbackQuery
from states.state import QuizStates
from keyboards.inline import topics_keyboard, after_answer_keyboard
from utils.quiz_generate import send_next_question, check_answer
from data.topics import TOPICS

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command('quiz'))
async def cmd_quiz(message: Message, state: FSMContext):
    await state.set_state(QuizStates.choosing_topic)

    try:
        photo = FSInputFile('images/quiz.png')
        await message.answer_photo(
            photo=photo,
            caption='<b>Квиз с ChatGPT</b>\nВыбери тему — и погнали',
            reply_markup=topics_keyboard(topics=TOPICS),
            parse_mode='html'
        )
    except Exception as e:
        logger.exception(f"Ошибка при отправке фото: {e}")
        await message.answer(
            '<b>Квиз с ChatGPT</b>\nВыбери тему — и погнали',
            reply_markup=topics_keyboard(topics=TOPICS),
            parse_mode='html'
        )


@router.callback_query(QuizStates.choosing_topic, F.data.startswith('quiz:topic:'))
async def on_topic_chosen(callback: CallbackQuery, state: FSMContext):
    topic_key = callback.data.split(':')[-1]
    if topic_key not in TOPICS:
        await callback.answer('Неизвестная тема')
        return

    topic = TOPICS[topic_key]
    await state.update_data(topic_key=topic_key, topic=topic, score=0, total=0, current_question='')
    await state.set_state(QuizStates.answering)

    await callback.answer(f'Тема {topic["name"]}')

    try:
        if callback.message.photo and callback.message.caption:
            await callback.message.edit_caption(
                caption=f'{topic["name"]} — отличный выбор! Генерирую вопрос'
            )
        elif callback.message.text:
            await callback.message.edit_text(
                text=f'{topic["name"]} — отличный выбор! Генерирую вопрос'
            )
        else:
            await callback.message.answer(f'{topic["name"]} — отличный выбор! Генерирую вопрос')
    except Exception as e:
        logger.exception(f"Ошибка при обновлении сообщения о выборе темы: {e}")
        await callback.message.answer(f'{topic["name"]} — отличный выбор! Генерирую вопрос')

    await send_next_question(callback.message, state, topic_key)


@router.message(QuizStates.answering, F.text)
async def cmd_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    current_question = data.get('current_question', '')
    score = data.get('score', 0)
    total = data.get('total', 0)

    if not current_question:
        await message.answer('Что-то пошло не так. Начни заново /quiz')
        await state.clear()
        return

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    is_correct, explanation = await check_answer(current_question, message.text)

    result_header = '✅ <b>Верно</b>' if is_correct else '⛔️ <b>Неверно</b>'
    if is_correct:
        score += 1
    total += 1

    await state.update_data(score=score, total=total, current_question='')

    await message.answer(
        f'{result_header}\n\n{explanation}\n\nСчет <b>{score}/{total}</b>',
        reply_markup=after_answer_keyboard(),
        parse_mode='html'
    )


@router.callback_query(F.data == 'quiz:next')
async def on_quiz_next(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    data = await state.get_data()
    topic_key = data.get('topic_key')
    await send_next_question(callback.message, state=state, topic_key=topic_key)


@router.callback_query(F.data == 'quiz:change_topic')
async def on_quiz_change_topic(callback: CallbackQuery, state: FSMContext):
    await state.set_state(QuizStates.choosing_topic)
    await state.update_data(score=0, total=0, current_question='')

    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer(
        'Выбери новую тему',
        reply_markup=topics_keyboard(TOPICS)
    )


@router.callback_query(F.data == 'quiz:stop')
async def on_quiz_stop(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get('score', 0)
    total = data.get('total', 0)

    await state.clear()
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    if total == 0:
        verdict = 'Ты не ответил ни на один вопрос'
    elif score == total:
        verdict = 'Идеальный результат'
    elif score / total >= 0.75:
        verdict = 'Отличный результат'
    elif score / total >= 0.4:
        verdict = 'Неплохо, есть куда расти!'
    else:
        verdict = 'Стоит подтянуть знания'

    await callback.message.answer(
        f'<b>Квиз завершен!</b>\n\nИтого: <b>{score} из {total}</b>\n\n{verdict}',
        parse_mode='html'
    )


@router.callback_query(F.data == 'quiz:cancel')
async def on_quiz_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()

    try:
        if callback.message.photo and callback.message.caption:
            await callback.message.edit_caption(caption='Квиз отменен')
        elif callback.message.text:
            await callback.message.edit_text(text='Квиз отменен')
        else:
            await callback.message.answer('Квиз отменен')
    except Exception as e:
        logger.exception(f"Ошибка при отмене Квиза: {e}")
import logging
from html import escape
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction
from states.state import GptStates
from services.openai_service import ask_gpt
from keyboards.inline import gpt_keyboard, main_menu

router = Router()
logger = logging.getLogger(__name__)

GPT_SYSTEM_PROMPT = (
    'Ты умный и дружелюбный ИИ-ассистент. '
    'Отвечай четко и по делу. '
    'Отвечай на том языке, на котором написан запрос'
)


@router.message(Command('gpt'))
async def cmd_gpt(message: Message, state: FSMContext):
    await state.set_state(GptStates.chatting)
    await state.update_data(history=[])

    try:
        photo = FSInputFile('images/gpt.png')
        await message.answer_photo(
            photo=photo,
            caption=(
                '<b>Режим ChatGPT</b>\n\n'
                'Напиши любой вопрос — я отвечу.\n'
                'Контекст диалога сохраняется.\n'
                'Нажми <b>Закончить</b>, чтобы выйти.'
            ),
            reply_markup=gpt_keyboard(),
            parse_mode='html'
        )
    except Exception as e:
        logger.exception(f"Ошибка при отправке фото: {e}")
        await message.answer(
            '<b>Режим ChatGPT</b>\n\n'
            'Напиши любой вопрос — я отвечу.\n'
            'Контекст диалога сохраняется.\n'
            'Нажми <b>Закончить</b>, чтобы выйти.',
            reply_markup=gpt_keyboard(),
            parse_mode='html'
        )


@router.message(GptStates.chatting, F.text)
async def cmd_gpt_message(message: Message, state: FSMContext):
    data = await state.get_data()
    history = data.get('history', [])

    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING
    )
    history.append({'role': 'user', 'content': message.text})

    try:
        response = await ask_gpt(
            user_message=message.text,
            system_prompt=GPT_SYSTEM_PROMPT,
            history=history
        )
    except Exception as e:
        logger.exception(f"Ошибка при обращении к GPT: {e}")
        response = 'Произошла ошибка при обращении к GPT. Попробуй еще раз.'


    history.append({'role': 'assistant', 'content': response})
    history = history[-20:]  # Ограничение истории до 20 сообщений
    await state.update_data(history=history)

    await message.answer(
        escape(response),
        reply_markup=gpt_keyboard(),
        parse_mode='html'
    )


@router.callback_query(F.data == 'gpt:stop')
async def on_gpt_stop(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer('Выхожу из режима ChatGPT')

    try:
        if callback.message.photo and callback.message.caption:
            await callback.message.edit_caption(
                caption='Режим ChatGPT завершен.',
                reply_markup=main_menu()
            )
        elif callback.message.text:
            await callback.message.edit_text(
                text='Режим ChatGPT завершен.',
                reply_markup=main_menu()
            )
        else:
            await callback.message.answer(
                'Режим ChatGPT завершен.',
                reply_markup=main_menu()
            )
    except Exception as e:
        logger.exception(f"Ошибка при завершении режима ChatGPT: {e}")
        await callback.message.answer(
            'Режим ChatGPT завершен.',
            reply_markup=main_menu()
        )
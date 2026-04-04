import tempfile
import logging

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, FSInputFile
from keyboards.inline import analysis_menu, main_menu
from states.state import ExcelStates
from aiogram.fsm.context import FSMContext
from services.openai_service import ai_analyze_dataframe
router = Router()
logger = logging.getLogger(__name__)


async def safe_send_photo(target, photo, caption):
    if isinstance(target, CallbackQuery):
        await target.message.answer_photo(photo=FSInputFile(photo), caption=caption)
    else:
        await target.answer_photo(photo=FSInputFile(photo), caption=caption)


@router.message(Command("chart"))
async def cmd_chart(message: Message, state: FSMContext):
    await state.update_data(action="chart")
    await state.set_state(ExcelStates.waiting_file)
    await message.answer("📂 Отправь Excel файл (.xlsx)")

@router.message(Command("ai"))
async def cmd_ai(message: Message):
    await generate_ai_analysis(message)

@router.message(Command("info"))
async def cmd_info(message: Message):
    await generate_info(message)


@router.callback_query(F.data.startswith("menu:analytics:"))
async def analytics_buttons(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    action = callback.data.split(":")[-1]

    if action in ["chart", "ai", "info"]:
        await state.update_data(action=action)
        await state.set_state(ExcelStates.waiting_file)

        await callback.message.answer(
            "📂 Отправь Excel файл (.xlsx)"
        )

    elif action == "back":
        await callback.message.answer(
            "⬅️ Возврат в главное меню",
            reply_markup=main_menu()
        )
@router.message(ExcelStates.waiting_file, F.document)
async def handle_excel(message: Message, state: FSMContext):
    data = await state.get_data()
    action = data.get("action")

    document = message.document

    if not document.file_name.endswith('.xlsx'):
        await message.answer("❌ Отправь Excel файл (.xlsx)")
        return

    file = await message.bot.get_file(document.file_id)

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        await message.bot.download_file(file.file_path, tmp.name)
        df = pd.read_excel(tmp.name)


    if action == "chart":
        await generate_chart_from_df(message, df)

    elif action == "ai":
        await message.answer("🤖 Анализирую...")
        analysis = await ai_analyze_dataframe(df)
        await message.answer(analysis)

    elif action == "info":
        text = df.describe().to_string()
        await message.answer(f"<pre>{text}</pre>", parse_mode="HTML")

    await state.clear()


async def generate_chart_from_df(message, df):
    if df.shape[1] < 2:
        await message.answer("❌ Нужно минимум 2 столбца")
        return

    plt.figure(figsize=(6, 4))
    sns.barplot(x=df.iloc[:, 0], y=df.iloc[:, 1])
    plt.xticks(rotation=45)
    plt.tight_layout()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as img:
        plt.savefig(img.name)
        plt.close()

        await message.answer_photo(
            FSInputFile(img.name),
            caption="📊 График построен!"
        )
async def generate_ai_analysis(target):
    await safe_send_photo(target, "images/ai.png", "🤖 AI Аналитика выполняется...")

    if isinstance(target, CallbackQuery):
        await target.message.answer(
            "⚡️ Здесь будет вывод AI анализа данных",
            reply_markup=analysis_menu()
        )
    else:
        await target.answer(
            "⚡️ Здесь будет вывод AI анализа данных",
            reply_markup=analysis_menu()
        )

async def generate_info(target):
    await safe_send_photo(target, "images/info.png", "📝 Сводка данных")

    if isinstance(target, CallbackQuery):
        await target.message.answer(
            "📋 Здесь будет текстовая сводка аналитики",
            reply_markup=analysis_menu()
        )
    else:
        await target.answer(
            "📋 Здесь будет текстовая сводка аналитики",
            reply_markup=analysis_menu()
        )

@router.callback_query(F.data == "menu:analytics:upload")
async def upload_excel(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "📂 Отправь Excel файл (.xlsx), и я построю график"
    )

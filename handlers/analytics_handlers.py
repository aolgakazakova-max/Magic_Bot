import logging
import os

import pandas as pd
import matplotlib.pyplot as plt

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext

from keyboards.inline import analytics_menu, main_menu
from states.state import ExcelStates
from services.openai_service import ai_analyze_dataframe

router = Router()
logger = logging.getLogger(__name__)



@router.callback_query(F.data == "menu:analytics")
async def open_analytics(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()

    await callback.message.answer(
        "📊 Аналитика:",
        reply_markup=analytics_menu()
    )



@router.callback_query(F.data == "excel:upload")
async def upload_excel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.set_state(ExcelStates.waiting_file)

    await callback.message.answer("📂 Отправь Excel файл (.xlsx)")



@router.message(ExcelStates.waiting_file, F.document)
async def handle_excel(message: Message, state: FSMContext):
    doc = message.document

    if not doc.file_name.endswith(".xlsx"):
        await message.answer("❌ Только .xlsx файл")
        return

    file = await message.bot.get_file(doc.file_id)

    tmp_path = f"excel_{message.from_user.id}.xlsx"

    await message.bot.download_file(file.file_path, tmp_path)

    # проверяем что файл реально читается
    try:
        pd.read_excel(tmp_path)
    except Exception:
        os.remove(tmp_path)
        await message.answer("❌ Не удалось прочитать Excel файл")
        return

    await state.update_data(file_path=tmp_path)
    await state.set_state(ExcelStates.choosing_action)

    await message.answer(
        "📊 Файл загружен!\nВыбери действие:",
        reply_markup=analytics_menu()
    )



@router.callback_query(F.data.startswith("excel:"), ExcelStates.choosing_action)
async def process_actions(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    action = callback.data.split(":")[1]
    data = await state.get_data()

    file_path = data.get("file_path")

    if not file_path or not os.path.exists(file_path):
        await callback.message.answer("⚠️ Файл не найден. Загрузите заново.")
        return

    df = pd.read_excel(file_path)



    if action == "chart":
        try:
            if df.shape[1] < 2:
                await callback.message.answer("❌ Нужно минимум 2 колонки")
                return

            x = df.iloc[:, 0]
            y = df.iloc[:, 1]

            chart_path = f"chart_{callback.from_user.id}.png"

            plt.figure(figsize=(8, 4))
            plt.plot(x, y, marker="o")
            plt.title("Excel Chart")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(chart_path)
            plt.close()

            await callback.message.answer_photo(
                FSInputFile(chart_path)
            )

            if os.path.exists(chart_path):
                os.remove(chart_path)

        except Exception as e:
            await callback.message.answer(f"⚠️ Ошибка графика: {e}")



    elif action == "ai":
        try:
            await callback.message.answer("🤖 Анализирую данные...")

            result = await ai_analyze_dataframe(df)

            await callback.message.answer(result)

        except Exception as e:
            await callback.message.answer(f"⚠️ Ошибка AI: {e}")



    elif action == "info":
        try:
            info = df.describe(include="all").to_string()
            await callback.message.answer(f"<pre>{info}</pre>")

        except Exception as e:
            await callback.message.answer(f"⚠️ Ошибка info: {e}")



    elif action == "upload":
        await state.set_state(ExcelStates.waiting_file)
        await callback.message.answer("📂 Отправь новый Excel файл")


    else:
        await callback.message.answer("⚠️ Неизвестное действие")



@router.callback_query(F.data == "menu:back")
async def back(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    file_path = data.get("file_path")
    if file_path and os.path.exists(file_path):
        os.remove(file_path)

    await state.clear()

    await callback.message.answer(
        "🏠 Главное меню",
        reply_markup=main_menu()
    )

    await callback.answer()
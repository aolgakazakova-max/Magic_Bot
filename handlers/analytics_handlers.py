import json
import tempfile
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from aiogram.fsm.context import FSMContext

from states.state import ExcelStates
from services.openai_service import ai_analyze_dataframe

router = Router()



@router.callback_query(F.data == "analytics:upload")
async def upload_excel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.clear()
    await state.set_state(ExcelStates.waiting_file)

    await callback.message.answer("📂 Отправь Excel файл (.xlsx)")



@router.message(ExcelStates.waiting_file, F.document)
async def handle_excel(message: Message, state: FSMContext):
    doc = message.document

    if not doc.file_name.endswith(".xlsx"):
        await message.answer("❌ Только .xlsx файлы")
        return

    file = await message.bot.get_file(doc.file_id)

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        await message.bot.download_file(file.file_path, tmp.name)
        df = pd.read_excel(tmp.name)


    await state.update_data(df_json=df.to_json())

    await state.set_state(ExcelStates.choosing_action)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 График", callback_data="excel:chart")],
        [InlineKeyboardButton(text="🤖 AI анализ", callback_data="excel:ai")],
        [InlineKeyboardButton(text="📝 Сводка", callback_data="excel:info")],
        [InlineKeyboardButton(text="📂 Загрузить заново", callback_data="analytics:upload")],
    ])

    await message.answer("📊 Выбери действие:", reply_markup=keyboard)



@router.callback_query(F.data.startswith("excel:"))
async def process_excel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()

    raw = data.get("df_json")
    if not raw:
        await callback.message.answer("❌ Сначала загрузи Excel файл")
        return


    df = pd.DataFrame(json.loads(raw))

    action = callback.data.split(":")[1]
    print("🔥 ACTION:", action)


    if action == "chart":
        try:
            df = df.head(10)

            if len(df.columns) < 2:
                await callback.message.answer("❌ Нужно минимум 2 столбца для графика")
                return

            x = df.iloc[:, 0]
            y = df.iloc[:, 1]

            plt.figure()
            plt.plot(x, y, marker="o")
            plt.xticks(rotation=45)
            plt.tight_layout()

            buf = BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            plt.close()

            photo = BufferedInputFile(buf.read(), filename="chart.png")

            await callback.message.answer_photo(
                photo=photo,
                caption="📊 Ваш график"
            )

        except Exception as e:
            await callback.message.answer(f"❌ Ошибка графика: {e}")



    elif action == "ai":
        await callback.message.answer("🤖 Анализирую данные...")
        result = await ai_analyze_dataframe(df)
        await callback.message.answer(result)



    elif action == "info":
        await callback.message.answer(
            f"<pre>{df.describe().to_string()}</pre>",
            parse_mode="HTML"
        )


    await state.clear()



@router.callback_query(F.data == "analytics:back")
async def back(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()

    await callback.message.answer("🏠 Главное меню")
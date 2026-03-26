import os
import tempfile
import logging
import asyncio
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from services.openai_service import ai_analyze_dataframe



router = Router()
logger = logging.getLogger(__name__)


def validate_dataframe(df: pd.DataFrame) -> str | None:
    if df.empty:
        return "❌ Файл пустой."
    if df.columns.empty:
        return "❌ В таблице нет заголовков (столбцов)."
    if df.memory_usage(deep=True).sum() > 5 * 1024 * 1024:
        return "❌ Файл слишком большой (лимит 5MB)."
    return None


@router.message(F.document)
async def handle_excel(message: Message, state: FSMContext):
    document = message.document

    if not document.file_name.endswith((".xlsx", ".xls")):
        await message.answer("❌ Отправь Excel файл (.xlsx или .xls)")
        return

    data = await state.get_data()
    action = data.get("action", "chart")

    await message.answer("📥 Загружаю и обрабатываю файл...")


    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        tmp_path = tmp_file.name

    try:
        file = await message.bot.get_file(document.file_id)
        await message.bot.download_file(file.file_path, tmp_path)
        df = await asyncio.to_thread(pd.read_excel, tmp_path)
        error_msg = validate_dataframe(df)
        if error_msg:
            await message.answer(error_msg)
            return
        if action == "ai":
            df_clean = df.dropna(how='all').iloc[:100, :15]
            await message.answer("🤖 Анализирую данные через AI...")
            # Вызов твоей функции анализа
            analysis = await ai_analyze_dataframe(df_clean)
            await message.answer(analysis)

        else:
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            all_cols = df.columns.tolist()

            if not numeric_cols:
                await message.answer("❌ В таблице нет числовых данных для графика.")
                return

            x_col = all_cols[0]
            y_col = numeric_cols[0] if numeric_cols[0] != x_col or len(numeric_cols) == 1 else numeric_cols[1]

            def create_plot_file():
                plt.switch_backend('Agg')
                plt.figure(figsize=(10, 6))

                plot_df = df.head(20).copy()
                if pd.api.types.is_numeric_dtype(plot_df[y_col]):
                    plot_df = plot_df.sort_values(by=y_col, ascending=False)

                sns.barplot(x=x_col, y=y_col, data=plot_df, palette="viridis")
                plt.xticks(rotation=45, ha='right')
                plt.title(f"ТОП-20: {y_col} по {x_col}")
                plt.tight_layout()

                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as img_tmp:
                    plt.savefig(img_tmp.name, dpi=150)
                    plt.close('all')
                    return img_tmp.name

            plot_path = await asyncio.to_thread(create_plot_file)
            await message.answer_photo(
                photo=FSInputFile(plot_path),
                caption=f"📊 График для '{y_col}' по '{x_col}'."
            )
            if os.path.exists(plot_path):
                os.remove(plot_path)

    except Exception as e:
        logger.exception("Ошибка при обработке")
        await message.answer("❌ Произошла ошибка при обработке файла.")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        await state.clear()

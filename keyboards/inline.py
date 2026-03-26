from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🎲 Случайный факт', callback_data='menu:random')],
        [InlineKeyboardButton(text='🤖 Chat GPT', callback_data='menu:gpt')],
        [InlineKeyboardButton(text='🗣️ Диалог с личностью', callback_data='menu:talk')],
        [InlineKeyboardButton(text='🎯 Квиз', callback_data='menu:quiz')],
        [InlineKeyboardButton(text='🔃 Переводчик', callback_data='menu:translate')],
        [InlineKeyboardButton(text='📈 Аналитика', callback_data='menu:analytics')],
    ])


def analysis_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Построить график", callback_data="menu:analytics:chart")],
        [InlineKeyboardButton(text="🤖 AI Аналитика", callback_data="menu:analytics:ai")],
        [InlineKeyboardButton(text="📝 Сводка данных", callback_data="menu:analytics:info")],
        [InlineKeyboardButton(text="📂 Загрузить Excel", callback_data="menu:analytics:upload")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu:analytics:back")]
    ])

def random_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🎲 Хочу еще факт', callback_data='random:again')],
            [InlineKeyboardButton(text='⛔️ Закончить', callback_data='random:stop')],
        ]
    )


def gpt_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Закончить', callback_data='gpt:stop')]
        ]
    )

def talk_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Сменить собеседника", callback_data="talk:change")],
        [InlineKeyboardButton(text="⛔️ Закончить", callback_data="talk:stop")]
    ]
    )

def persons_keyboard(persons):
    buttons = [
        [InlineKeyboardButton(text=f'{data["emoji"]} {data["name"]}', callback_data=f'talk:person:{key}')]
        for key, data in persons.items()
    ]
    buttons.append([InlineKeyboardButton(text='⛔️ Отмена', callback_data='talk:cancel')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def translate_keyboard() -> InlineKeyboardMarkup:

    buttons = [
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="trans:ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="trans:en")],
        [InlineKeyboardButton(text="🇫🇷 Français", callback_data="trans:fr")],
        [InlineKeyboardButton(text="⛔️ Отмена", callback_data="trans:cancel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def topics_keyboard(topics: dict) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=data['name'], callback_data=f'quiz:topic:{key}')]
        for key, data in topics.items()
    ]
    buttons.append([InlineKeyboardButton(text='⛔️ Отмена', callback_data='quiz:cancel')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def after_answer_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='▶️ Следующий вопрос', callback_data=f'quiz:next')],
            [InlineKeyboardButton(text='🔄 Сменить тему', callback_data=f'quiz:change_topic')],
            [InlineKeyboardButton(text='🛑 Закончить Квиз', callback_data=f'quiz:stop')],
        ]
    )
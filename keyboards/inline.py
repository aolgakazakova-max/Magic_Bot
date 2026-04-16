from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🎲 Случайный факт', callback_data='menu:random')],
        [InlineKeyboardButton(text='🤖 Chat GPT', callback_data='menu:gpt')],
        [InlineKeyboardButton(text='🗣️ Диалог', callback_data='menu:talk')],
        [InlineKeyboardButton(text='🎯 Квиз', callback_data='menu:quiz')],
        [InlineKeyboardButton(text='🔃 Перевод', callback_data='menu:translate')],
        [InlineKeyboardButton(text='📈 Аналитика', callback_data='menu:analytics')],
        [InlineKeyboardButton(text='ℹ️ Инфо', callback_data='menu:help')],
    ])


def random_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🎲 Ещё факт', callback_data='random:again')],
        [InlineKeyboardButton(text='🏠 В меню', callback_data='menu:back')],
    ])


def gpt_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='⛔ Завершить GPT', callback_data='gpt:stop')],
        [InlineKeyboardButton(text='🏠 В меню', callback_data='menu:back')],
    ])


def talk_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Сменить", callback_data="talk:change")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="menu:back")]
    ])


def persons_keyboard(persons: dict):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{data['emoji']} {data['name']}",
                callback_data=f"talk:person:{key}"
            )
        ]
        for key, data in persons.items()
    ] + [
        [InlineKeyboardButton(text="🏠 В меню", callback_data="menu:back")]
    ])


def topics_keyboard(topics: dict):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=data['name'],
                callback_data=f"quiz:topic:{key}"
            )
        ]
        for key, data in topics.items()
    ] + [
        [InlineKeyboardButton(text="🏠 В меню", callback_data="menu:back")]
    ])


def after_answer_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='▶️ Следующий', callback_data='quiz:next')],
        [InlineKeyboardButton(text='🏠 В меню', callback_data='menu:back')],
    ])


def analytics_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 График", callback_data="excel:chart")],
        [InlineKeyboardButton(text="🤖 AI анализ", callback_data="excel:ai")],
        [InlineKeyboardButton(text="📄 Инфо", callback_data="excel:info")],
        [InlineKeyboardButton(text="📂 Загрузить Excel", callback_data="excel:upload")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="menu:back")]
    ])


def translate_language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="translate:ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="translate:en")],
        [InlineKeyboardButton(text="🇫🇷 Français", callback_data="translate:fr")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="menu:back")]
    ])


def help_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 В меню", callback_data="menu:back")],
    ])
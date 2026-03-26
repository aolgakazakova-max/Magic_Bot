from aiogram.fsm.state import State, StatesGroup


class GptStates(StatesGroup):
    chatting = State()


class TalkStates(StatesGroup):
    choosing_person = State()
    chatting = State()


class QuizStates(StatesGroup):
    choosing_topic = State()
    answering = State()


class TranslateStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_language = State()

class ExcelStates(StatesGroup):
    waiting_file = State()


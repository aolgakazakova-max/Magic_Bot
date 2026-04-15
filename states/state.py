from aiogram.fsm.state import State, StatesGroup



class ExcelStates(StatesGroup):
    waiting_file = State()
    choosing_action = State()



class GptStates(StatesGroup):
    chatting = State()




class TalkStates(StatesGroup):
    choosing_person = State()
    chatting = State()




class QuizStates(StatesGroup):
    choosing_topic = State()
    answering = State()




class TranslateStates(StatesGroup):
    choosing_language = State()
    waiting_text = State()

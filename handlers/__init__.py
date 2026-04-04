from aiogram import Router
from handlers.commands_handler import router as commands_router
from handlers.random_fact import router as random_fact_router
from handlers.gpt_chat import router as gpt_router
from handlers.talk import router as talk_router
from handlers.quiz import router as quiz_router
from handlers.translator import router as translator_router
from handlers.analytics_handlers import router as analytics_router
from handlers.excel_analytics_handlers import router as excel_router


router = Router()

router.include_routers(commands_router, random_fact_router,
                       gpt_router, talk_router, quiz_router,translator_router,analytics_router,excel_router )





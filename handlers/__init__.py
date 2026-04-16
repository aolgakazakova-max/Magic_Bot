from aiogram import Router

from handlers.commands_handler import router as commands_router
from handlers.random_fact import router as random_router
from handlers.gpt_chat import router as gpt_router
from handlers.talk import router as talk_router
from handlers.quiz import router as quiz_router
from handlers.analytics_handlers import router as analytics_router
from handlers.translate_handler import router as translate_router

router = Router(name="main_router")

router.include_router(translate_router)
router.include_router(commands_router)
router.include_router(gpt_router)
router.include_router(talk_router)
router.include_router(quiz_router)
router.include_router(random_router)
router.include_router(analytics_router)




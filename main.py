from aiogram import Bot, Dispatcher
import asyncio
import logging
from config import BOT_TOKEN
from handlers import router
from aiogram.client.default import DefaultBotProperties


async def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    bot = Bot(token=BOT_TOKEN,default=DefaultBotProperties(parse_mode='html'))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)



if __name__ == '__main__':
    asyncio.run(main())



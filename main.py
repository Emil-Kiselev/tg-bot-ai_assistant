import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart

from bot.handlers import router

bot = Bot("YOUR_API")
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)


@dp.message(CommandStart())
async def start_cmd(message: Message):
    await message.reply("Welcome! 🤖💛!\nType what are you interested in")

async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

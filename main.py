import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.types import CallbackQuery
from os import getenv
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from core.handlers import handler, questionary, send_messages, menu_handler, pay_handler, referal_link, \
    activate_promocode, check_every_day

router = Router()

load_dotenv()
dp = Dispatcher()
token = getenv('TOKEN')
admin_id = getenv("ADMIN_ID")


async def del_content(bot: Bot, content_id, chat_id):
    await bot.delete_message(chat_id, message_id=content_id)


async def start_bot(bot: Bot):
    await bot.send_message(admin_id, text="Бот запущен")


async def stop_bot(bot: Bot):
    await bot.send_message(admin_id, text="Бот остановлен")


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=token, parse_mode='HTML')
    dp.include_routers(handler.router, questionary.router, send_messages.router, router, menu_handler.router,
                       pay_handler.router, activate_promocode.router, referal_link.router
                       )

    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_every_day.send_messages_to_active_subscribers, args=[bot], trigger='cron',
                      day_of_week='mon,tue,wed,thu,fri,sat,sun', hour=8, minute=22)
    scheduler.add_job(check_every_day.update_subscriptions, args=[bot], trigger='cron',
                      day_of_week='mon,tue,wed,thu,fri,sat,sun',
                      hour=8, minute=29)
    scheduler.start()
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

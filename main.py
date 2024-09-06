import asyncio # библиотека для асинхронныйх звпросов
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils import executor
from datetime import datetime, timedelta

import pytz # для работы с часовыми поясами


API_TOKEN = "PASTE_API_TOKEN_HERE"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

alarms = {} # Хранение будильников тут

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет, я бот-будильник сделанный Лизой. Используйте /set HH:MM для установки будильника")


@dp.message_handler(commands=['set'])
async def set_alarm(message: types.Message):
    try:
        time_str = message.text.split()[1]
        alarm_time = datetime.strptime(time_str, '%H:%M').time()
        tz = pytz.timezone('Europe/Moscow') # потом можно дописать функцию выбора часового пояса по умолчанию будет мск
        now = datetime.now(tz)
        alarm_datetime = datetime.combine(now.date(), alarm_time).replace(tzinfo=tz)
        print(alarm_datetime, type(alarm_datetime), now, type(now))
        if alarm_datetime < now:
            alarm_datetime += timedelta(days=1) # установить на следующий день если время уже прошло

        # сохраняем будильник
        alarms[message.from_user.id] = alarm_datetime
        await message.answer(f"Будильник установлен на {alarm_time.strftime('%H:%M')}.")
    except (IndexError, ValueError):
        await message.answer("Ой, похоже вы ввели неправильный формат времени используйте HH:MM")


# функция будильник
async def alarm_notifier():
    tz = pytz.timezone("Europe/Moscow")
    print(f"функция будильника запустилась")
    while True:
        now = datetime.now(tz)
        print(f"цикл вайл погнал")
        for user_id, alarm_time in list(alarms.items()):
            print(f"для {user_id} и времени {alarm_time} а сейчас {now}")
            if now + timedelta(minutes=30) >= alarm_time: # костыль почему-то часовой пояс из pytz теряет 30 минут....
                print(f"Будильник сработал у {user_id}")
                await bot.send_message(user_id, "Пора вставать!")
                del alarms[user_id]
        await asyncio.sleep(30) # перерыв 30 секунд

if __name__ == "__main__": # Базовая конструкция для якобы основной функции
    loop = asyncio.get_event_loop()
    loop.create_task(alarm_notifier())
    executor.start_polling(dp, skip_updates=True)

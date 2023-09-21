import asyncio
import os
import threading
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
import cv2, numpy as np
import time
from dotenv import load_dotenv

load_dotenv()

class AlarmBot:
      # Замените на свой chat_id
    
    def __init__(self, bot_token):
        self.bot = Bot(token=bot_token)
        self.dp = Dispatcher(self.bot)
        # Глобальные переменные для хранения состояния и времени последнего ответа
        self.alarm_state = False
        self.last_response_time = None
        self.CHAT_ID = 290302339

    async def start(self):
        await self.bot.send_message(self.CHAT_ID, "Бот запущен. Ожидание команды /start")

    async def send_message_with_image(self, chat_id, message_text, image_path):
        with open(image_path, 'rb') as image_file:
            await self.bot.send_photo(chat_id, photo=image_file, caption=message_text, parse_mode=ParseMode.MARKDOWN)

    async def send_periodic_messages(self):
        chat_id = self.CHAT_ID # Замените на свой chat_id

        while self.alarm_state:
            if self.last_response_time is None or (time.time() - self.last_response_time) > 900:
                message_text = "Прошло 15 минут. Продолжаю отправку."
                image_path = 'your_image.jpg'  # Замените на путь к вашему изображению
                await self.send_message_with_image(chat_id, message_text, image_path)
                await asyncio.sleep(n)  # Замените n на интервал отправки в секундах
            else:
                await asyncio.sleep(60)  # Проверяем состояние каждую минуту

    async def handle_start(self, message):
        self.alarm_state = True
        self.last_response_time = None
        await message.reply("Привет! Теперь вы будете получать периодические уведомления. Для остановки напишите 'Ok'.")

    async def handle_stop(self, message):
        self.alarm_state = False
        self.last_response_time = time.time()
        await message.reply("Вы отменили уведомления.")

    def run(self):
        from aiogram import executor

        async def on_startup(dp):
            await self.start()

        self.dp.register_message_handler(self.handle_start, commands=['start'])
        self.dp.register_message_handler(self.handle_stop, lambda message: message.text.lower() == 'ok')

        executor.start_polling(self.dp, skip_updates=True, on_startup=on_startup)

def main_bot_thread():
    bot_token = os.getenv("BOT_TOKEN")
    bot = AlarmBot(bot_token)
    bot.run()

if __name__ == '__main__':
    # Запуск бота в отдельном потоке
    bot_thread = threading.Thread(target=main_bot_thread)
    bot_thread.start()
    
    image = 

    # Основной цикл программы
    while True:
        # Ваша основная логика здесь
        # Пример:
        print("Основной цикл программы...")
        time.sleep(60)  # Пауза на 60 секунд
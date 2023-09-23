from aiogram import Bot, Dispatcher, types
import logging
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

class Telebot:
    def __init__(self, bot, dp, chat_id):
        self.bot = bot
        self.dp = dp
        self.chat_id = chat_id

    async def send_hello(self):
        logging.info(f'Hello from telebot')
        await self.bot.send_message(self.chat_id, text='Poopsik says hello')

    async def send_msg(self, msg, user_id, img_data):
        logging.info(f'Send msg to: {user_id}')
        await self.bot.send_photo(user_id, img_data, msg)
        await asyncio.sleep(10)

    async def handle_message(self, message: types.Message):
        self.user_id = message.from_user.id
        logging.info(f'Telebot user_id: {self.user_id}')
        await self.bot.send_message(chat_id=self.user_id, text=f"Your user_id is: {self.user_id}")

    async def start(self, message: types.Message):
        # Отправляем пользователю его user_id
        await message.reply(f"Ваш user_id: {message.from_user.id}")


bot = Bot(os.getenv('BOT_TOKEN'))
chat_id = os.getenv('CHAT_ID')
dp = Dispatcher(bot)
telebot = Telebot(bot, dp, chat_id)

dp.register_message_handler(telebot.handle_message)
dp.register_message_handler(telebot.start, commands=['start'])

async def main():
    await dp.start_polling()
    while True:
        await telebot.send_hello()
        await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())
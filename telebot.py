from aiogram import Bot, Dispatcher
import logging
import asyncio

class Telebot:
    def __init__(self, token):
        self._bot = Bot(token)
        dp = Dispatcher(self._bot)
        
        @dp.message_handler()
        async def handle_message(self, message):
            user_id = message.from_user.id
            await self._bot.send_message(chat_id=user_id, text=f"Your user_id is: {user_id}")
        
    async def send_hello(self):
        await self._bot.send_message(chat_id='290302339', text='Poopsik says hello')
        
    async def send_msg(self, msg, user_id, img_data):
        logging.info(f'Send msg to: {user_id}')
        await self._bot.send_photo(user_id, img_data, msg['description'])
        asyncio.sleep(10)
        

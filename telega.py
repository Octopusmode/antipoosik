import asyncio
from aiogram import Bot, Dispatcher, types
import os


class TelegramBot:
    def __init__(self, token: str = None):
        self.__TOKEN__ = token
        self.bot = Bot(token=self.__TOKEN__)
        self.dp = Dispatcher()
        self.halt_sending = False
    
    async def start(self, message: types.Message):
        await message.answer('Hello, world!')
        
    def run(self):
        self.dp.register_message_handler(self.start, commands=['start'])
        self.dp.start_polling()
        # self.dp.run_polling()
        
    async def repeat_message(self, message: str, chat_id: int = 0, interval: int = 60):
        while not self.halt_sending:
            await self.bot.send_message(chat_id=chat_id, text=message)
            await asyncio.sleep(interval)
            
    async def handle_messages(self, message: types.Message):
        print(f'{message=}')
        if message.text.lower() == 'ok' or message.text.lower() == u'ок':
            await self.bot.send_message(message.from_user.id, 'Okay, messages halted')
        
        
        
        

        


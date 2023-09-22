from aiogram import Bot, dispatcher
from dotenv import load_dotenv
import logging
import os

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

print(BOT_TOKEN)
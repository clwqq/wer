import logging
from aiogram.enums import ParseMode
from aiogram import *
from aiogram.types import *
from aiogram.client.bot import *
from aiogram.filters import *
from aiogram.utils.keyboard import *
from aiogram.types.input_media_photo import *
from aiogram.filters.callback_data import *
from aiogram.exceptions import *
import sqlite3
import asyncio
import datetime
from datetime import datetime, timedelta
from collections import defaultdict
import calendar
from decimal import Decimal, ROUND_HALF_UP
import time
import openpyxl
from openpyxl.utils import get_column_letter
from collections import defaultdict
import re
import os
from io import BytesIO

SAVE_DIR = "pic"

TOKEN = '7946866733:AAG_HOBF1AKE7BRXYWAPPCPOdUds-rbczLk'

dp = Dispatcher()

@dp.message(lambda message: message.photo and message.caption)
async def handle_photo(message):
    # Получаем текст подписи для имени файла
    file_name = message.caption
    # Получаем фото (берем самое большое по размеру изображение)
    photo = message.photo[-1]
    # Получаем файл изображения
    file = await bot.get_file(photo.file_id)
    file_path = file.file_path
    
    # Создаем путь для сохранения
    file_extension = ".jpg"
    save_path = os.path.join(SAVE_DIR, file_name + file_extension)
    
    # Скачиваем и сохраняем файл
    await bot.download_file(file_path, save_path)
    
    await message.answer(f"Фото сохранено как {file_name}{file_extension}")

async def main():
    global bot
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    asyncio.run(main())



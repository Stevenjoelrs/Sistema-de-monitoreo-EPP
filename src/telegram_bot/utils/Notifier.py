import os
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("ALERT_CHAT_ID")
bot = Bot(token=TOKEN)

async def notify_group(message: str):
    await bot.send_message(chat_id=CHAT_ID, text=message)

async def send_report(image, message: str):
    await bot.send_message(chat_id=CHAT_ID, text=message)
    if image:
        image.seek(0) 
        await bot.send_photo(chat_id=CHAT_ID, photo=image)
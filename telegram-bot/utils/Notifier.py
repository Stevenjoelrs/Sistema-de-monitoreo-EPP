import os
from telegram import Bot
from dotenv import load_dotenv
from model import Report

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("ALERT_CHAT_ID")
bot = Bot(token=TOKEN)

@staticmethod
async def notify_group(message: str):
    await bot.send_message(chat_id=CHAT_ID, text=message)
    
@staticmethod
async def send_report(report: Report):
    pass

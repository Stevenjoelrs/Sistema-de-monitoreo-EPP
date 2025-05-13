from telegram import Update
from telegram.ext import ContextTypes

class PingController:
    
    @staticmethod
    async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("pong")
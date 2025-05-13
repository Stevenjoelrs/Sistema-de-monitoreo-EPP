import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram_bot.controller.PingController import PingController
from telegram_bot.controller.StartController import StartController

def iniciar_bot():
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", StartController.start))
    application.add_handler(CommandHandler("ping", PingController.ping))
    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    

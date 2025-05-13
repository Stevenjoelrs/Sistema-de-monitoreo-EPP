import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from controller.PingController import PingController
from controller.StartController import StartController

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

application = ApplicationBuilder().token(TOKEN).build()
application.add_handler( CommandHandler("start", StartController.start))
application.add_handler( CommandHandler("ping", PingController.ping))
application.run_polling(allowed_updates=Update.ALL_TYPES)
from telegram import Update
from telegram.ext import ContextTypes

class StartController:
    
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "👷‍♂️ ¡Hola! Yo soy @EPPDetectionSystemBot.\n"
            "🛑 Me encargo de alertar sobre faltas de seguridad detectando la ausencia de Equipos de Protección Personal (EPP) en tiempo real.\n"
            "✅ Estoy aquí para ayudarte a mantener tu entorno laboral más seguro."
        )
from utils import Run_Async_Task
from telegram_bot.utils.Notifier import send_report

class Report:
    def __init__(self, image, message):
        self.image = image
        self.message = message    
    
    async def enviar_reporte(self):
        await send_report(self.image, self.message)
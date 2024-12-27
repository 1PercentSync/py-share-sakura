from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from database import create_or_update_user, refresh_user_token
import asyncio

class TelegramBot:
    def __init__(self, token: str):
        self.application = Application.builder().token(token).build()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("token", self.token_command))
        self.application.add_handler(CommandHandler("refresh", self.refresh_token_command))

    async def run(self):
        await self.application.initialize()
        await self.application.start()
        await self.application.run_polling()

if __name__ == "__main__":
    bot = TelegramBot("YOUR_BOT_TOKEN")
    asyncio.run(bot.run())

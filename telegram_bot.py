from telegram import Update
from telegram.ext import Application, CommandHandler
from database import create_or_update_user, refresh_user_token
import asyncio

class TelegramBot:
    def __init__(self, token: str):
        self.application = Application.builder().token(token).build()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.help_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("register", self.register_command))
        self.application.add_handler(CommandHandler("refresh", self.refresh_command))
        self.application.add_handler(CommandHandler("userdata", self.userdata_command))
        self.application.add_handler(CommandHandler("globaldata", self.globaldata_command))

    async def run(self):
        await self.application.initialize()
        await self.application.start()
        await self.application.run_polling()

if __name__ == "__main__":
    bot = TelegramBot("YOUR_BOT_TOKEN")
    asyncio.run(bot.run())

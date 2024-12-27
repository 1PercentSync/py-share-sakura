import textwrap
from telegram import Update
from telegram.ext import Application, CommandHandler
from database import create_or_update_user, refresh_user_token, get_user_info
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

    async def help_command(self, update: Update, context):
        # Create help message with all available commands
        help_text = textwrap.dedent("""
        🌸 Sakura Share 机器人使用指南:

        /register - 注册账户/获取token/更新显示名称
        /refresh - 更换新的token
        /userdata - 查看自己的数据
        /globaldata - 查看全局统计
        """)
        # Send help message to user
        await update.message.reply_text(help_text)

    async def register_command(self, update: Update, context):
        # Check if the message is from a private chat
        if update.effective_chat.type != "private":
            await update.message.reply_text("⚠️ 请通过私聊注册！点击 @SakuraShareBot 开始私聊。")
            return
        
        # Get user info
        user_id = update.effective_user.id
        # Combine first_name and last_name with a space
        display_name = update.effective_user.first_name
        if update.effective_user.last_name:
            display_name += f" {update.effective_user.last_name}"
        
        # Create or update user and get token
        token = create_or_update_user(user_id, display_name)
        
        # Generate access URL
        access_url = f"https://sakura-share.one/{user_id}-{token}"
        
        # Create response message with clickable token and URL
        response = textwrap.dedent(f"""
            ✅ 注册成功！

            🔑 Token: `{user_id}-{token}`
            🔗 访问地址: `{access_url}`

            点击以上内容可复制
            """)
        
        # Send message with markdown parsing enabled for clickable code blocks
        await update.message.reply_text(response, parse_mode="Markdown")

    async def refresh_command(self, update: Update, context):
        # Check if the message is from a private chat
        if update.effective_chat.type != "private":
            await update.message.reply_text("⚠️ 请通过私聊刷新token！点击 @SakuraShareBot 开始私聊。")
            return
        
        # Get user info
        user_id = update.effective_user.id
        
        # Refresh token
        new_token = refresh_user_token(user_id)
        
        if new_token is None:
            await update.message.reply_text("❌ 请先使用 /register 注册账户！")
            return
        
        # Generate new access URL
        access_url = f"https://sakura-share.one/{user_id}-{new_token}"
        
        # Create response message with clickable token and URL
        response = textwrap.dedent(f"""
            ✅ Token已更新！

            🔑 新Token: `{user_id}-{new_token}`
            🔗 新访问地址: `{access_url}`

            点击以上内容可复制
        """)
        
        # Send message with markdown parsing enabled for clickable code blocks
        await update.message.reply_text(response, parse_mode="Markdown")

    async def userdata_command(self, update: Update, context):
        # Get user ID
        user_id = update.effective_user.id
        
        # Get user info from database
        user_info = get_user_info(user_id)
        
        if user_info is None:
            await update.message.reply_text("❌ 请先使用 /register 注册账户！")
            return
        
        # Format user data message
        user_data_text = textwrap.dedent(f"""
        📊 您的数据统计：

        👤 显示名称：{user_info['telegram_name']}
        
        📈 数据统计：
        • 贡献值：{user_info['contribution']}
        • 可用积分：{user_info['credit']}
        • 总使用量：{user_info['total_usage']}
        • 今日使用：{user_info['daily_usage']}
        """)
        
        # Send message with markdown parsing enabled
        await update.message.reply_text(user_data_text, parse_mode="Markdown")

if __name__ == "__main__":
    bot = TelegramBot("YOUR_BOT_TOKEN")
    asyncio.run(bot.run())

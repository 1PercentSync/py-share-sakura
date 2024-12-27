import textwrap
from telegram import Update
from telegram.ext import Application, CommandHandler
from database import create_or_update_user, refresh_user_token, get_user_info, get_top_contributors, get_top_credits, get_top_total_usage, get_top_daily_usage
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

    async def set_commands(self):
        """Set the bot's command list that appears in the menu"""
        commands = [
            ("help", "显示帮助信息"),
            ("register", "注册账户/获取token/更新显示名称"),
            ("refresh", "更换新的token"),
            ("userdata", "查看自己的数据"),
            ("globaldata", "查看全局统计")
        ]
        await self.application.bot.set_my_commands(commands)

    async def run(self):
        # Set commands before starting the bot
        await self.set_commands()
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
    
    async def globaldata_command(self, update: Update, context):
        # Get top 5 users for each category
        top_contributors = get_top_contributors(5)
        top_credits = get_top_credits(5)
        top_total_usage = get_top_total_usage(5)
        top_daily_usage = get_top_daily_usage(5)
        
        # Format rankings into text
        def format_ranking(title: str, data: list, unit: str = "") -> str:
            text = f"\n{title}："
            for i, (name, value) in enumerate(data, 1):
                text += f"\n{i}. {name}: {value}{unit}"
            return text
        
        # Create global statistics message
        global_stats = textwrap.dedent(f"""
        📊 全局统计数据
        
        🏆 贡献榜{format_ranking("贡献值排行", top_contributors)}
        
        💰 积分榜{format_ranking("积分排行", top_credits)}
        
        📈 总用量榜{format_ranking("总用量排行", top_total_usage)}
        
        📊 今日用量榜{format_ranking("今日用量排行", top_daily_usage)}
        """)
        
        # Send message
        await update.message.reply_text(global_stats)
    
    

if __name__ == "__main__":
    bot = TelegramBot("7866348862:AAGTbajWm4aV4gqHTSyh94gImIZ8rGHP2_I")
    bot.set_commands()
    bot.application.run_polling()
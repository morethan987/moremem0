import botpy
from botpy.types.message import Message
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

import os

# 获取环境变量
BOT_APPID = os.getenv("BOT_APPID")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_APPID or not BOT_TOKEN:
    raise ValueError("请在 .env 文件中设置 BOT_APPID 和 BOT_TOKEN")

class QQBot(botpy.Client):
    def __init__(self, intents = botpy.Intents.default(), timeout = 5, is_sandbox=False, log_config = None, log_format = None, log_level = None, bot_log = True, ext_handlers = True):
        super().__init__(intents, timeout, is_sandbox, log_config, log_format, log_level, bot_log, ext_handlers)

    async def on_at_message(self, message: Message):
        """
        当收到 @ 机器人的消息时触发
        """
        # 构造消息内容
        msg = f"你好，{message.author.username}! 我收到了你的消息: {message.content}"

        # 发送回复消息
        await self.api.post_message(
            channel_id=message.channel_id,
            content=msg
        )

def run_bot():
    # 创建机器人实例
    bot = QQBot()
    # 启动机器人
    bot.run(appid=BOT_APPID, token=BOT_TOKEN)

import os
import re
import collections

import discord
from discord.ext import commands, tasks

from modules.Logger import Logger
from modules.Config import Config
from modules.llm.main import LLM

intents = discord.Intents.default()
intents.message_content = True

def clean_message(content):
    cleaned_text = re.sub(r'<@&?\d+>', '', content)
    return cleaned_text

class DiscordBot(commands.Bot):
    def __init__(self, logger: Logger, config: Config, llm: LLM) -> None:
        super().__init__(
            command_prefix='/',
            intents=intents,
            help_command=None,
        )
        self.logger = logger
        self.config = config
        self.llm = llm
        self.channel_context = {}

        self.logger.info(f"discord.py API версия: {discord.__version__}")

    async def load_cogs(self) -> None:
        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"modules.discord.cogs.{extension}")
                    self.logger.info(f"Загружено расширение '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(f"Не удалось загрузить расширение {extension}\n{exception}")

    @tasks.loop(minutes=1.0)
    async def status_task(self) -> None:
        await self.change_presence(activity=discord.CustomActivity(name="Што"))

    @status_task.before_loop
    async def before_status_task(self) -> None:
        await self.wait_until_ready()

    async def setup_hook(self) -> None:
        self.logger.info(f"Авторизован как {self.user.name}")

        await self.load_cogs()
        self.status_task.start()

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user or message.author.bot:
            return
        if not message.channel.permissions_for(message.guild.me).send_messages:
            return
        if message.channel.id not in self.channel_context:
            self.channel_context[message.channel.id] = collections.deque(
                maxlen=self.config.context_max_len
            )
        self.channel_context[message.channel.id].append(message)

        if self.user in message.mentions:
            async with message.channel.typing():
                messages = [
                    {
                        "role": message.author.id == self.user.id and "assistant" or "user",
                        "content": clean_message(message.content),
                    }
                    for message in self.channel_context[message.channel.id]
                ]

                messages.insert(0, {
                    "role": "system",
                    "content": self.config.system_message,
                })
                output_message = self.llm.generate(messages, self.user)

                if output_message:
                    await message.channel.send(output_message[:2000], reference=message)
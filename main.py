import platform
import os

from modules.Config import Config
from modules.Logger import Logger
from modules.discord.main import DiscordBot
from modules.llm.main import LLM

CONFIG_PATH = f"{os.path.realpath(os.path.dirname(__file__))}/config.json"

Logger("system").info(f"Запущено на: {platform.system()} {platform.release()} ({os.name})")

config = Config(Logger("config"), CONFIG_PATH)
llm = LLM(Logger("LLM"), config)

(DiscordBot(Logger("discord"), config, llm)
    .run(config.token, log_handler=None)
)

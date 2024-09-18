import platform
import os

from modules.Config import Config
from modules.Logger import Logger
from modules.discord.main import DiscordBot
from modules.llm.main import LLM

logger = Logger("system")
logger.info(f"Запущено на: {platform.system()} {platform.release()} ({os.name})")

config = Config(Logger("config"), f"{os.path.realpath(os.path.dirname(__file__))}/config.json")
llm = LLM(config, logger)

(DiscordBot(Logger("discord"), config, llm)
    .run(config.token, log_handler=None)
)

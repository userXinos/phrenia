from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Context


class LLM(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(description="Установить температуру семплирования")
    @app_commands.describe(value="Тепература")
    async def temp(self, context: Context, value: float) -> None:
        pass

async def setup(bot) -> None:
    await bot.add_cog(LLM(bot))
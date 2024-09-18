from discord.ext import commands
from discord import app_commands, Interaction


class LLM(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(description="Установить температуру семплирования")
    @app_commands.describe(value="Тепература")
    async def temp(self, ctx: Interaction, value: float) -> None:
        self.bot.config.temperature = value
        await ctx.response.send_message(f"Температура семплирования установлена на `{self.bot.config.temperature}`")

    @app_commands.command(description="Установить системный промт")
    @app_commands.describe(message="Сообщение")
    async def prompt(self, ctx: Interaction, message: str) -> None:
        self.bot.config.system_message = message
        await ctx.response.send_message(f"Системный промт: `{self.bot.config.system_message}`")

async def setup(bot) -> None:
    await bot.add_cog(LLM(bot))
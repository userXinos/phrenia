import discord
from discord import app_commands
from discord.ext import commands

cog_path = 'modules.discord.cogs'

class Owner(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(description="Сихронизировать слэш команды")
    @app_commands.describe(scope="Контекст сихронизации")
    @app_commands.choices(scope=[
        app_commands.Choice(name='global', value=0),
        app_commands.Choice(name='guild', value=1),
    ])
    @commands.is_owner()
    async def sync(self, ctx: discord.Interaction, scope: int) -> None:
        if scope == 0:
            await self.bot.tree.sync()
            embed = discord.Embed(
                description="Слеш команды были сихронизированы в глобальном контексте",
                color=0xBEBEFE,
            )
            await ctx.response.send_message(embed=embed)
        elif scope == 1:
            self.bot.tree.copy_global_to(guild=ctx.guild)
            await self.bot.tree.sync(guild=ctx.guild)
            embed = discord.Embed(
                description="Слеш команды были сихронизированы в этой гильдии",
                color=0xBEBEFE,
            )
            await ctx.response.send_message(embed=embed)

    @app_commands.command(description="Рассихронизирует слэш команды")
    @app_commands.describe(scope="Контекст сихронизации")
    @app_commands.choices(scope=[
        app_commands.Choice(name='global', value=0),
        app_commands.Choice(name='guild', value=1),
    ])
    @commands.is_owner()
    async def unsync(self, ctx: discord.Interaction, scope: int) -> None:
        if scope == 0:
            self.bot.tree.clear_commands(guild=None)
            await self.bot.tree.sync()
            embed = discord.Embed(
                description="Слеш команды были рассинхронизированы в глобальном контексте",
                color=0xBEBEFE,
            )
            await ctx.response.send_message(embed=embed)
        elif scope == 1:
            self.bot.tree.clear_commands(guild=ctx.guild)
            await self.bot.tree.sync(guild=ctx.guild)
            embed = discord.Embed(
                description="Слеш команды были рассинхронизированы в этой гильдии",
                color=0xBEBEFE,
            )
            await ctx.response.send_message(embed=embed)

    @app_commands.command(description="Загрузка cog")
    @app_commands.describe(cog="Имя cog для загрузки")
    @commands.is_owner()
    async def load(self, ctx: discord.Interaction, cog: str) -> None:
        try:
            await self.bot.load_extension(f"{cog_path}.{cog}")
        except Exception:
            embed = discord.Embed(
                description=f"Не удалось загрузить cog `{cog}`", color=0xE02B2B
            )
            await ctx.response.send_message(embed=embed)
            return
        embed = discord.Embed(
            description=f"Успешно загружен cog `{cog}`", color=0xBEBEFE
        )
        await ctx.response.send_message(embed=embed)

    @app_commands.command(description="Выгрузка cog")
    @app_commands.describe(cog="Имя cog для выгрузки")
    @commands.is_owner()
    async def unload(self, ctx: discord.Interaction, cog: str) -> None:
        try:
            await self.bot.unload_extension(f"{cog_path}.{cog}")
        except Exception:
            embed = discord.Embed(
                description=f"Не удалось выгрузить cog `{cog}`", color=0xE02B2B
            )
            await ctx.response.send_message(embed=embed)
            return
        embed = discord.Embed(
            description=f"Успешно выгружен cog `{cog}`", color=0xBEBEFE
        )
        await ctx.response.send_message(embed=embed)

    @app_commands.command(description="Перезагрузка cog")
    @app_commands.describe(cog="Имя cog для перезагрузки")
    @commands.is_owner()
    async def reload(self, ctx: discord.Interaction, cog: str) -> None:
        try:
            await self.bot.reload_extension(f"{cog_path}.{cog}")
        except Exception:
            embed = discord.Embed(
                description=f"Не удалось перезагрузить cog `{cog}`", color=0xE02B2B
            )
            await ctx.response.send_message(embed=embed)
            return
        embed = discord.Embed(
            description=f"Успешно перезагружен cog `{cog}`", color=0xBEBEFE
        )
        await ctx.response.send_message(embed=embed)

    @app_commands.command(description="Выключение бота")
    @commands.is_owner()
    async def shutdown(self, ctx: discord.Interaction) -> None:
        embed = discord.Embed(description="Выключается. Пока! :wave:", color=0xBEBEFE)
        await ctx.response.send_message(embed=embed)
        await self.bot.close()

    @app_commands.command(description="Отправка сообщения ботом")
    @app_commands.describe(message="Сообщение, которое будет повторено ботом")
    @commands.is_owner()
    async def say(self, ctx: discord.Interaction, *, message: str) -> None:
        await ctx.response.send_message.send_message(message)

    @app_commands.command(description="Отправка embed ботом")
    @app_commands.describe(message="Сообщение, которое будет повторено ботом")
    @commands.is_owner()
    async def embed(self, ctx: discord.Interaction, *, message: str) -> None:
        embed = discord.Embed(description=message, color=0xBEBEFE)
        await ctx.response.send_message(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(Owner(bot))
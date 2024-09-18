import discord
from discord import app_commands, Interaction
from discord.ext import commands

cog_path = 'modules.discord.cogs'

# noinspection PyUnresolvedReferences
# Interaction.response.send_message - чет не видит
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
    async def sync(self, ctx: Interaction, scope: int) -> None:
        if scope == 0:
            self.bot.tree.clear_commands(guild=None)
            await self.bot.tree.sync()
            await ctx.response.send_message("Слеш команды были сихронизированы в глобальном контексте", ephemeral=True)
        elif scope == 1:
            self.bot.tree.clear_commands(guild=ctx.guild)
            self.bot.tree.copy_global_to(guild=ctx.guild)
            await self.bot.tree.sync(guild=ctx.guild)
            await ctx.response.send_message("Слеш команды были сихронизированы в этой гильдии", ephemeral=True)

    @app_commands.command(description="Рассихронизирует слэш команды")
    @app_commands.describe(scope="Контекст сихронизации")
    @app_commands.choices(scope=[
        app_commands.Choice(name='global', value=0),
        app_commands.Choice(name='guild', value=1),
    ])
    @commands.is_owner()
    async def unsync(self, ctx: Interaction, scope: int) -> None:
        if scope == 0:
            self.bot.tree.clear_commands(guild=None)
            await self.bot.tree.sync()
            await ctx.response.send_message("Слеш команды были рассинхронизированы в глобальном контексте", ephemeral=True)
        elif scope == 1:
            self.bot.tree.clear_commands(guild=ctx.guild)
            await self.bot.tree.sync(guild=ctx.guild)
            await ctx.response.send_message("Слеш команды были рассинхронизированы в этой гильдии", ephemeral=True)

    @app_commands.command(description="Загрузка cog")
    @app_commands.describe(cog="Имя cog для загрузки")
    @commands.is_owner()
    async def load(self, ctx: Interaction, cog: str) -> None:
        try:
            await self.bot.load_extension(f"{cog_path}.{cog}")
        except Exception:
            await ctx.response.send_message(f"Не удалось загрузить cog `{cog}`", ephemeral=True)
            return
        await ctx.response.send_message(f"Успешно загружен cog `{cog}`", ephemeral=True)

    @app_commands.command(description="Выгрузка cog")
    @app_commands.describe(cog="Имя cog для выгрузки")
    @commands.is_owner()
    async def unload(self, ctx: Interaction, cog: str) -> None:
        try:
            await self.bot.unload_extension(f"{cog_path}.{cog}")
        except Exception:
            await ctx.response.send_message(f"Не удалось выгрузить cog `{cog}`", ephemeral=True)
            return
        await ctx.response.send_message(f"Успешно выгружен cog `{cog}`", ephemeral=True)

    @app_commands.command(description="Перезагрузка cog")
    @app_commands.describe(cog="Имя cog для перезагрузки")
    @commands.is_owner()
    async def reload(self, ctx: Interaction, cog: str) -> None:
        try:
            await self.bot.reload_extension(f"{cog_path}.{cog}")
        except Exception:
            await ctx.response.send_message(f"Не удалось перезагрузить cog `{cog}`", ephemeral=True)
            return
        await ctx.response.send_message(f"Успешно перезагружен cog `{cog}`", ephemeral=True)

    @app_commands.command(description="Выключение бота")
    @commands.is_owner()
    async def shutdown(self, ctx: Interaction) -> None:
        await ctx.response.send_message("Выключается. Пока! :wave:")
        await self.bot.close()

    @app_commands.command(description="Отправка сообщения ботом")
    @app_commands.describe(message="Сообщение, которое будет повторено ботом")
    @commands.is_owner()
    async def say(self, ctx: Interaction, *, message: str) -> None:
        await ctx.response.send_message(message)

    @app_commands.command(description="Отправка embed ботом")
    @app_commands.describe(message="Сообщение, которое будет повторено ботом")
    @commands.is_owner()
    async def embed(self, ctx: Interaction, *, message: str) -> None:
        embed = discord.Embed(description=message, color=0xBEBEFE)
        await ctx.response.send_message(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(Owner(bot))
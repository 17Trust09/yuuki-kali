import discord
from discord.ext import commands
import os
import database

bot_owner = [530391227753955338, 306862417185472512]

def is_bot_owner():
    async def predicate(ctx):
        return ctx.author.id in bot_owner
    return commands.check(predicate)

class CogManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="load_cog")
    @is_bot_owner()
    async def load_cog(self, ctx, cog_name):
        try:
            await self.bot.load_extension(f"cogs.{cog_name}")
            database.update_cog_status(ctx.guild.id, cog_name, True)
            await ctx.send(f"{cog_name} Cog wurde geladen.")
        except Exception as e:
            await ctx.send(f"Fehler beim Laden des {cog_name} Cogs: {e}")

    @commands.command(name="unload_cog")
    @is_bot_owner()
    async def unload_cog(self, ctx, cog_name):
        try:
            await self.bot.unload_extension(f"cogs.{cog_name}")
            database.update_cog_status(ctx.guild.id, cog_name, False)
            await ctx.send(f"{cog_name} Cog wurde entladen.")
        except Exception as e:
            await ctx.send(f"Fehler beim Entladen des {cog_name} Cogs: {e}")

    @commands.command(name="list_cogs")
    @commands.is_owner()
    async def list_cogs(self, ctx):
        """Listet alle Cogs und ihren Status für den aktuellen Server."""
        guild_id = str(ctx.guild.id)
        cogs_status = database.get_all_cogs_status(guild_id)

        embed = discord.Embed(title="Server-spezifischer Cog-Status",
                              description="Liste aller Cogs und ihr Status auf diesem Server:",
                              color=discord.Color.blue())
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                cog_name = filename[:-3]
                status = cogs_status.get(cog_name)
                status_text = "✅ Geladen" if status else "❌ Ungeladen"
                embed.add_field(name=cog_name, value=status_text, inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="toggle_cog")
    @is_bot_owner()
    async def toggle_cog(self, ctx, cog_name):
        """Lädt oder entlädt einen Cog."""
        cog_path = f"cogs.{cog_name}"
        try:
            if self.bot.get_cog(cog_name):
                await self.bot.unload_extension(cog_path)
                print(f"Unloading cog: {ctx.guild.id}, {cog_name}")  # Debugging-Print
                database.update_cog_status(ctx.guild.id, cog_name, False)
                await ctx.send(f"{cog_name} wurde entladen.")
            else:
                await self.bot.load_extension(cog_path)
                print(f"Loading cog: {ctx.guild.id}, {cog_name}")  # Debugging-Print
                database.update_cog_status(ctx.guild.id, cog_name, True)
                await ctx.send(f"{cog_name} wurde geladen.")
        except Exception as e:
            await ctx.send(f"Fehler beim Laden/Entladen von {cog_name}: {e}")

    @commands.command(name="load_all_cogs")
    @is_bot_owner()
    async def load_all_cogs(self, ctx):
        """Lädt alle Cogs."""
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                cog_name = filename[:-3]
                try:
                    await self.bot.load_extension(f"cogs.{cog_name}")
                    database.update_cog_status(ctx.guild.id, cog_name, True)
                    await ctx.send(f"{cog_name} Cog wurde geladen.")
                except Exception as e:
                    await ctx.send(f"Fehler beim Laden des {cog_name} Cogs: {e}")

    @commands.command(name="unload_all_cogs")
    @is_bot_owner()
    async def unload_all_cogs(self, ctx):
        """Entlädt alle Cogs, außer CogManagement."""
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                cog_name = filename[:-3]

                # Überspringe CogManagement
                if cog_name == "CogManagement":
                    continue

                try:
                    await self.bot.unload_extension(f"cogs.{cog_name}")
                    database.update_cog_status(ctx.guild.id, cog_name, False)
                    await ctx.send(f"{cog_name} Cog wurde entladen.")
                except Exception as e:
                    await ctx.send(f"Fehler beim Entladen des {cog_name} Cogs: {e}")

async def setup(bot):
    await bot.add_cog(CogManagement(bot))

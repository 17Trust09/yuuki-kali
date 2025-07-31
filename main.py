import discord
from discord.ext import commands
import setting
import os
import database
import logging
from logging_config import setup_logging
from custom_logging_handler import setup_custom_logging

# Logging-Konfiguration
setup_logging()

# Bot-Initialisierung
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

# Die Funktion, die das Präfix für jede Nachricht bestimmt
async def get_prefix(bot, message):
    # Standard-Präfix, falls die Nachricht in DMs gesendet wurde
    default_prefix = '!'

    # Überprüfen, ob die Nachricht in einem Server (nicht in DMs) gesendet wurde
    if message.guild is None:
        return default_prefix

    server_id = str(message.guild.id)
    prefix = database.get_server_setting(server_id)
    return prefix or default_prefix

# Initialisieren des Bots mit der Präfix-Funktion und Intents
bot = commands.Bot(command_prefix=get_prefix, intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is ready as {bot.user}')
    database.create_tables()
    setup_custom_logging(bot)

    # Debug: Liste aller Gilden ausgeben
    for guild in bot.guilds:
        print(f'Connected to guild: {guild.name} (ID: {guild.id})')

    # Laden aller Cogs im cogs-Verzeichnis
    for cog_file in setting.COGS_DIR.glob("*.py"):
        if cog_file.stem != "__init__":
            cog_name = cog_file.stem
            try:
                await bot.load_extension(f"cogs.{cog_name}")
                print(f"{cog_name} successfully loaded.")
            except discord.ext.commands.errors.ExtensionAlreadyLoaded:
                pass
            except Exception as e:
                logging.getLogger('discord').exception(f"Failed to load {cog_name}: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return  # Ignoriere CommandNotFound Fehler
    logging.getLogger('discord').error(f'Error in command {ctx.command}: {error}')
    await ctx.send(f'An error occurred: {error}')

@bot.event
async def on_error(event_method, *args, **kwargs):
    logging.getLogger('discord').error(f'Unhandled exception in {event_method}', exc_info=True)

# Beispiel für einen Befehl, der die Einstellungen ändert
@bot.command()
@commands.has_permissions(administrator=True)
async def setprefix(ctx, *, prefix):
    server_id = str(ctx.guild.id)
    database.update_server_setting(server_id, prefix)
    await ctx.send(f'Präfix wurde auf {prefix} gesetzt.')

# Testbefehl, der einen Fehler verursacht
@bot.command()
async def error_command(ctx):
    1 / 0  # Division durch null verursacht einen Fehler

# Bot starten
bot.run(setting.TOKEN)

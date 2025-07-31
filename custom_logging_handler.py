import logging
import discord
import setting


class DiscordLoggingHandler(logging.Handler):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    def emit(self, record):
        log_entry = self.format(record)
        user = self.bot.get_user(setting.BOT_OWNER_ID)
        if user:
            embed = discord.Embed(
                title="Log Alert",
                description=log_entry,
                color=discord.Color.red() if record.levelno >= logging.ERROR else discord.Color.orange()
            )
            embed.add_field(name="Logger Name", value=record.name, inline=False)
            embed.add_field(name="Level", value=record.levelname, inline=False)
            embed.add_field(name="Message", value=record.getMessage(), inline=False)
            embed.timestamp = discord.utils.snowflake_time(self.bot.user.id)

            self.bot.loop.create_task(user.send(embed=embed))


def setup_custom_logging(bot):
    handler = DiscordLoggingHandler(bot)
    handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logging.getLogger('discord').addHandler(handler)

import discord
from discord.ext import commands
from collections import defaultdict
import time
import asyncio
import database  # Stellen Sie sicher, dass database.py im gleichen Verzeichnis liegt

class antispam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_message_times = defaultdict(list)

    async def is_spamming(self, user_id, guild_id):
        settings = database.get_spam_settings(guild_id)
        if not settings:
            return False

        message_limit, time_limit = settings
        recent_messages = self.user_message_times[user_id][-message_limit:]

        is_spam = len(recent_messages) == message_limit and recent_messages[-1] - recent_messages[0] < time_limit
        return is_spam

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setspamsettings(self, ctx, message_limit: int, time_limit: int):
        guild_id = str(ctx.guild.id)
        database.set_spam_settings(guild_id, message_limit, time_limit)
        await ctx.send(f"Anti-Spam-Einstellungen aktualisiert: {message_limit} Nachrichten in {time_limit} Sekunden.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or isinstance(message.channel, discord.DMChannel):
            return

        self.user_message_times[message.author.id].append(time.time())

        if await self.is_spamming(message.author.id, message.guild.id):
            muted_role = discord.utils.get(message.guild.roles, name="Muted")
            if muted_role:
                await message.author.add_roles(muted_role)
                await message.channel.send(f"{message.author.mention}, bitte nicht spammen. Du wurdest für 5 Minuten stumm geschaltet!")
                del self.user_message_times[message.author.id]

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if "Muted" in [role.name for role in after.roles] and "Muted" not in [role.name for role in before.roles]:
            await asyncio.sleep(300)  # 5 Minuten warten
            if "Muted" in [role.name for role in after.roles]:
                await after.remove_roles(discord.utils.get(after.guild.roles, name="Muted"))


async def setup(bot):
    await bot.add_cog(antispam(bot))

import discord
from discord.ext import commands, tasks
import random
import asyncio
import database

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.give_online_xp.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        user_id = str(message.author.id)
        guild_id = str(message.guild.id)
        xp, level = database.get_user_level(user_id, guild_id)

        # XP für gesendete Nachricht hinzufügen
        xp += 5
        level_up = False
        if xp >= (level + 1) * 100:
            level += 1
            level_up = True

        database.update_user_level(user_id, guild_id, xp, level)

        if level_up:
            level_channel_id = database.get_level_channel(str(message.guild.id))
            if level_channel_id:
                level_channel = message.guild.get_channel(int(level_channel_id))
                if level_channel:
                    await level_channel.send(f"{message.author.mention}, du bist jetzt Level {level}!")
                else:
                    await message.channel.send(
                        f"{message.author.mention}, du bist jetzt Level {level}! (Hinweis: Der festgelegte Level-Kanal wurde nicht gefunden.)")
            else:
                await message.channel.send(
                    f"{message.author.mention}, du bist jetzt Level {level}! (Hinweis: Es wurde kein Level-Kanal festgelegt.)")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_leveling(self, ctx, channel: discord.TextChannel):
        database.set_level_channel(str(ctx.guild.id), str(channel.id))
        await ctx.send(f"Level-Up-Nachrichten werden nun in {channel.mention} gesendet.")

    @commands.command()
    async def level(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user_id = str(member.id)
        guild_id = str(ctx.guild.id)
        xp, level = database.get_user_level(user_id, guild_id)
        next_level_xp = (level + 1) * 100

        embed = discord.Embed(title=f"Level & XP von {member.name}", color=discord.Color.blue())
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="Level", value=str(level), inline=True)
        embed.add_field(name="XP", value=f"{xp}/{next_level_xp}", inline=True)

        progress = int((xp / next_level_xp) * 10)
        bar = ["⬜"] * 10
        for i in range(progress):
            bar[i] = "🟩"
        embed.add_field(name="Fortschritt", value="".join(bar), inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def leaderboard(self, ctx):
        guild_id = str(ctx.guild.id)
        leaderboard_data = database.get_leaderboard(guild_id)
        leaderboard = ""
        for i, (user_id, xp, level) in enumerate(leaderboard_data[:10], start=1):
            user = self.bot.get_user(int(user_id))
            if user:
                leaderboard += f"{i}. {user.mention} - Level {level} with {xp} XP\n"

        embed = discord.Embed(
            title="🏆 **Leaderboard** 🏆",
            description=leaderboard,
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

    @tasks.loop(seconds=1)  # Kurzes Intervall, um die Loop zu starten
    async def give_online_xp(self):
        await asyncio.sleep(random.uniform(300, 900))
        for guild in self.bot.guilds:
            if not guild.chunked:
                members = await guild.fetch_members(limit=None).flatten()
            else:
                members = guild.members

            for member in members:
                if member.status in [discord.Status.online, discord.Status.idle, discord.Status.dnd] and not member.bot:
                    user_id = str(member.id)
                    guild_id = str(guild.id)
                    xp, level = database.get_user_level(user_id, guild_id)

                    xp += 2  # Beispiel: 2 XP alle 10 Minuten
                    level_up = False
                    if xp >= (level + 1) * 100:
                        level += 1
                        level_up = True

                    database.update_user_level(user_id, guild_id, xp, level)

    @give_online_xp.before_loop
    async def before_give_online_xp(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Leveling(bot))

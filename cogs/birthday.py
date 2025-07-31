import discord
from discord.ext import commands
import database
from datetime import datetime
from discord.ext import commands, tasks

class birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_birthdays.start()

    @commands.command(name='addbirthday')
    async def add_birthday(self, ctx, user: discord.Member, date: str):
        # Überprüfen des Datumsformats
        try:
            birthday = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            await ctx.send(embed=discord.Embed(description="Falsches Datumformat. Bitte im Format JJJJ-MM-TT angeben.", color=discord.Color.red()))
            return

        # Hinzufügen des Geburtstags zur Datenbank
        database.add_birthday(ctx.guild.id, user.id, birthday)
        await ctx.send(embed=discord.Embed(description=f"Geburtstag von {user.mention} für den {birthday} hinzugefügt.", color=discord.Color.green()))

    @commands.command(name='removebirthday')
    async def remove_birthday(self, ctx, member: discord.Member):
        # Entfernen des Geburtstags aus der Datenbank
        database.remove_birthday(ctx.guild.id, member.id)
        await ctx.send(embed=discord.Embed(description=f"Geburtstag von {member.mention} entfernt.", color=discord.Color.green()))


    @tasks.loop(hours=24)
    async def check_birthdays(self):
        today = datetime.now().date()
        birthdays = database.get_todays_birthdays(today)

        for guild_id, user_id in birthdays:
            guild = self.bot.get_guild(guild_id)
            if guild:
                member = guild.get_member(user_id)
                if member:
                    channel = guild.system_channel  # oder einen anderen Kanal wählen
                    if channel:
                        await channel.send(embed=discord.Embed(description=f"🎉 Alles Gute zum Geburtstag, {member.mention}! 🎂", color=discord.Color.blue()))

    @check_birthdays.before_loop
    async def before_check_birthdays(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(birthday(bot))

import discord
from discord.ext import commands
import datetime
import re
import database

class feedback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def feedback(self, ctx, *, feedback_message: str):
        safe_filename = re.sub(r'[<>:"/\\|?*]', '', ctx.guild.name)
        filename = f"{safe_filename}.txt"

        # Speichern des Feedbacks in der Datenbank
        database.save_feedback(str(ctx.guild.id), ctx.guild.name, feedback_message)

        # Sende das Feedback als Embed an den Bot-Besitzer
        embed = discord.Embed(title=f"Feedback from {ctx.guild.name}", color=discord.Color.blue())
        embed.add_field(name="Server ID", value=ctx.guild.id, inline=False)
        embed.add_field(name="Date & Time", value=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), inline=False)
        embed.add_field(name="Feedback", value=feedback_message, inline=False)

        owner = self.bot.get_user(530391227753955338)  # Owner ID
        if owner:
            await owner.send(embed=embed)

        await ctx.send("Vielen Dank für Ihr Feedback! Es wurde an den Bot-Ersteller gesendet.")

async def setup(bot):
    bot.owner_id = 530391227753955338  # Ersetzen Sie dies durch Ihre tatsächliche Owner ID
    await bot.add_cog(feedback(bot))
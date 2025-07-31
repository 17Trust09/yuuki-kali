import discord
from discord.ext import commands

class poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="poll", help="Erstellt eine Umfrage in einem bestimmten Kanal. Format: !poll #Kanal Frage ; Option 1 ; Option 2 ; ... ; Option N")
    async def create_poll(self, ctx, channel: discord.TextChannel, *, args):
        args = args.split(" ; ")
        if len(args) < 2:
            await ctx.send("Bitte stelle eine Frage und gib mindestens zwei Optionen an. Trenne Frage und Optionen mit ' ; '")
            return

        question = args[0]
        options = args[1:]
        if len(options) > 10:
            await ctx.send("Zu viele Optionen! Bitte gib nicht mehr als 10 Optionen an.")
            return

        reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

        description = []
        for x, option in enumerate(options):
            description += '\n\n{} {}'.format(reactions[x], option)

        embed = discord.Embed(title=question, description=''.join(description), color=0x00FF00)

        try:
            react_message = await channel.send(embed=embed)
            for reaction in reactions[:len(options)]:
                await react_message.add_reaction(reaction)
            embed.set_footer(text='Umfrage-ID: {}'.format(react_message.id))
            await react_message.edit(embed=embed)
        except discord.Forbidden:
            await ctx.send(f"Ich habe keine Berechtigung, um in {channel.mention} zu posten.")
        except Exception as e:
            await ctx.send(f"Ein Fehler ist aufgetreten: {e}")

async def setup(bot):
    await bot.add_cog(poll(bot))
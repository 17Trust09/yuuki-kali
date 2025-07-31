import discord
from discord.ext import commands

class EmbedCreator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="createembed", help="Erstellt eine Einbettung. Format: !createembed Titel ; Beschreibung ; Farbe ; Fußzeile" "Beispiel:!createembed Mein Titel ; Dies ist eine Beschreibung ; FF5733 ; Dies ist eine Fußzeile")
    async def create_embed(self, ctx, *, args):
        args = args.split(" ; ")
        if len(args) < 4:
            await ctx.send("Bitte gib einen Titel, eine Beschreibung, eine Farbe und eine Fußzeile an. Trenne diese mit ' ; '")
            return

        title, description, color, footer = args
        color = int(color, 16)  # Umwandlung des Hexadezimalfarbcodes in einen Integer

        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text=footer)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EmbedCreator(bot))

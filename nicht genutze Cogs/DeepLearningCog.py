import discord
from discord.ext import commands
from transformers import pipeline

class DeepLearningCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.classifier = pipeline('sentiment-analysis')

    @commands.command()
    async def sentiment(self, ctx, *, text: str):
        try:
            result = self.classifier(text)
            sentiment = result[0]['label']
            confidence = result[0]['score']
            await ctx.send(f"Sentiment: {sentiment} with a confidence of {confidence:.2f}")
        except Exception as e:
            await ctx.send("An error occurred while processing your request.")
            print(e)

# Wichtig: Diese Funktion muss in jeder Cog-Datei vorhanden sein
async def setup(bot):
    await bot.add_cog(DeepLearningCog(bot))
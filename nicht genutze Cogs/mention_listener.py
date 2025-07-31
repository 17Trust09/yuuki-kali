import discord
from discord.ext import commands
import setting


class MentionListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # Liste der Synonyme
        synonyms = ['Icekey', 'icekey', 'IceKey', 'ICEKEY', 'Ice', 'ice', 'ICY', 'icy']
        if any(synonym in message.content for synonym in synonyms):
            try:
                user = await self.bot.fetch_user(setting.BOT_OWNER_ID)
                if user:
                    # Erstellen des Links zur Nachricht
                    message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"

                    # Erstellen des Embeds
                    embed = discord.Embed(
                        title="Mention Alert",
                        description=f"{message.author} mentioned you in {message.channel.mention}",
                        color=discord.Color.blue()
                    )
                    embed.add_field(name="Server", value=message.guild.name, inline=False)
                    embed.add_field(name="Message", value=message.content, inline=False)
                    embed.add_field(name="Link", value=f"[Jump to message]({message_link})", inline=False)
                    embed.set_footer(text=f"User ID: {message.author.id}")

                    await user.send(embed=embed)
                else:
                    print(f"User with ID {setting.BOT_OWNER_ID} not found.")
            except Exception as e:
                print(f"Failed to fetch user with ID {setting.BOT_OWNER_ID}: {e}")


async def setup(bot):
    await bot.add_cog(MentionListener(bot))

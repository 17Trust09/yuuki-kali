import discord
from discord.ext import commands, tasks
import datetime
import database

class giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_giveaway_messages.start()

    @tasks.loop(seconds=60)  # oder ein anderes geeignetes Intervall
    async def update_giveaway_messages(self):
        try:
            active_giveaways = database.get_active_giveaways()
            for giveaway in active_giveaways:
                guild_id, message_id, channel_id, prize, end_time_str = giveaway
                end_time = datetime.datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')

                if datetime.datetime.now() >= end_time:
                    guild = self.bot.get_guild(int(guild_id))
                    if guild:
                        channel = guild.get_channel(int(channel_id))
                        if channel:
                            try:
                                message = await channel.fetch_message(int(message_id))
                                # Hier können Sie die Nachricht aktualisieren oder Gewinner bekannt geben
                                await message.edit(content="Das Gewinnspiel ist beendet!")
                                # Gewinnspiel aus der Datenbank entfernen
                                database.remove_giveaway(guild_id, message_id)
                            except Exception as e:
                                print(f"Fehler beim Aktualisieren der Gewinnspiel-Nachricht: {e}")
        except Exception as e:
            print(f"Fehler in der update_giveaway_messages Loop: {e}")

    @commands.command(name="startgiveaway")
    @commands.has_permissions(administrator=True)
    async def start_giveaway(self, ctx, duration: int, *, prize: str):
        """Startet ein Gewinnspiel."""
        # Berechnung des Endzeitpunkts als datetime-Objekt
        end_time = datetime.datetime.now() + datetime.timedelta(minutes=duration)

        embed = discord.Embed(title="🎉 Gewinnspiel!",
                              description=f"Preis: {prize}\n\nReagiere mit 🎉, um teilzunehmen!",
                              color=discord.Color.gold())
        embed.set_footer(text=f"Endet in: {duration} Minuten")
        message = await ctx.send(embed=embed)
        await message.add_reaction("🎉")

        # Speichert das Gewinnspiel in der Datenbank
        database.create_giveaway(ctx.guild.id, message.id, ctx.channel.id, prize,
                                 end_time.strftime('%Y-%m-%d %H:%M:%S'))

    @commands.command(name="drawwinner")
    @commands.has_permissions(administrator=True)
    async def draw_winner(self, ctx, message_id: int):
        """Zieht einen Gewinner für das Gewinnspiel."""
        giveaway = database.get_giveaway(ctx.guild.id, message_id)
        if giveaway:
            message = await ctx.channel.fetch_message(giveaway['message_id'])
            users = await message.reactions[0].users().flatten()
            users.remove(self.bot.user)
            winner = random.choice(users)
            await ctx.send(
                embed=discord.Embed(description=f"🎉 Der Gewinner ist: {winner.mention}\nPreis: {giveaway['prize']}",
                                    color=discord.Color.green()))
            database.end_giveaway(ctx.guild.id, message.id)
        else:
            await ctx.send(embed=discord.Embed(description="Gewinnspiel nicht gefunden.", color=discord.Color.red()))


    @update_giveaway_messages.before_loop
    async def before_update_giveaway_messages(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(giveaway(bot))

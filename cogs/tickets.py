import discord
from discord.ext import commands
import database

class tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_or_create_transcript_channel(self, guild, member):
        ticket_settings = database.get_ticket_settings(str(guild.id))
        if not ticket_settings or None in ticket_settings:
            print("Keine Ticket-Einstellungen für diesen Server gefunden.")
            return

        ticket_message_id, mod_role_id = ticket_settings

        sanitized_name = f"{member.name}-log"
        transcript_channel = discord.utils.get(guild.text_channels, name=sanitized_name)
        if not transcript_channel:
            transcript_category = discord.utils.get(guild.categories, name="Ticket Log")
            if not transcript_category:
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.get_role(mod_role_id): discord.PermissionOverwrite(read_messages=True),
                    member: discord.PermissionOverwrite(read_messages=True)
                }
                transcript_category = await guild.create_category("Ticket Log", overwrites=overwrites)
            transcript_channel = await guild.create_text_channel(sanitized_name, category=transcript_category)
        return transcript_channel

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return

        guild = self.bot.get_guild(payload.guild_id)
        ticket_settings = database.get_ticket_settings(str(guild.id))

        if not ticket_settings or None in ticket_settings:
            print("Keine Ticket-Einstellungen für diesen Server gefunden.")
            return

        ticket_message_id, mod_role_id = ticket_settings

        if payload.message_id == ticket_message_id and str(payload.emoji) == "🎫":
            category = discord.utils.get(guild.categories, name="Tickets")
            if not category:
                category = await guild.create_category("Tickets")
            member = guild.get_member(payload.user_id)

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                member: discord.PermissionOverwrite(read_messages=True),
                guild.get_role(mod_role_id): discord.PermissionOverwrite(read_messages=True)
            }

            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

            channel = await guild.create_text_channel(f"ticket-{member.name}-{member.id}", category=category,
                                                      overwrites=overwrites)
            embed = discord.Embed(title="Ticket erstellt",
                                  description=f"Ticket für {member.mention}. Reagiere mit 🔒, um das Ticket zu schließen.",
                                  color=discord.Color.green())
            ticket_message = await channel.send(embed=embed)
            await ticket_message.add_reaction("🔒")

            await message.remove_reaction(payload.emoji, member)

        # Ticket schließen
        elif str(payload.emoji) == "🔒":
            channel = guild.get_channel(payload.channel_id)
            if channel and channel.name.startswith("ticket-"):
                ticket_user_id = int(channel.name.split('-')[-1])
                if payload.user_id == ticket_user_id or guild.get_member(
                        payload.user_id).guild_permissions.administrator:
                    transcript_channel = await self.get_or_create_transcript_channel(guild, payload.member)

                    transcript = ""
                    async for message in channel.history(oldest_first=True):
                        timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
                        transcript += f"{timestamp} - {message.author.name}: {message.content}\n"

                    chunks = [transcript[i:i + 2045] for i in range(0, len(transcript), 2045)]
                    for chunk in chunks:
                        embed = discord.Embed(title=f"Transkript für {payload.member.name}", description=chunk,
                                              color=discord.Color.orange())
                        await transcript_channel.send(embed=embed)
                    await channel.delete(reason="Ticket geschlossen")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_ticket_message(self, ctx, message_id: int):
        database.set_ticket_message_id(str(ctx.guild.id), message_id)
        await ctx.send(f"Ticket-Nachricht für {ctx.guild.name} gesetzt.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create_ticket_message(self, ctx, mod_role: discord.Role):
        support_category = discord.utils.get(ctx.guild.categories, name="Support")
        if not support_category:
            support_category = await ctx.guild.create_category("Support")

        support_channel = None
        if support_category.text_channels:
            support_channel = support_category.text_channels[0]
        else:
            support_channel = await ctx.guild.create_text_channel("ich-brauche-hilfe", category=support_category)

        embed = discord.Embed(title="Ticket System",
                              description="Reagiere auf diese Nachricht, um ein Ticket zu erstellen!",
                              color=discord.Color.blue())
        message = await support_channel.send(embed=embed)
        await message.add_reaction("🎫")

        database.set_ticket_settings(str(ctx.guild.id), message.id, mod_role.id)
        await ctx.send(
            f"Ticket-Nachricht in {support_channel.mention} erstellt und gespeichert. Mod-Rolle: {mod_role.name}")

async def setup(bot):
    await bot.add_cog(tickets(bot))
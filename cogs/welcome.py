import discord
from discord.ext import commands
import database


class welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        welcome_channel_id, _, _, _ = database.get_welcome_settings(guild_id)
        if welcome_channel_id:
            channel = self.bot.get_channel(int(welcome_channel_id))
        else:
            channel = discord.utils.get(member.guild.text_channels, name="👋eingangshalle")
        if channel:
            avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
            embed = discord.Embed(color=discord.Color.blue(), description=f"Willkommen auf dem Server, {member.mention}! Bitte lies die 📜regeln und reagiere darauf, um Zugriff auf den Server zu erhalten.")
            embed.set_author(name=member.name, icon_url=avatar_url)
            embed.set_thumbnail(url=avatar_url)
            embed.set_footer(text="Willkommen!")

            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild_id = str(payload.guild_id)
        _, rules_channel_id, member_role_id, rules_message_id = database.get_welcome_settings(guild_id)
        # Print statements zur Überprüfung
        #print(f"Reaction added: {payload.emoji}, Guild ID: {guild_id}, Channel ID: {payload.channel_id}, Message ID: {payload.message_id}")
        #print(f"Expected Channel ID: {rules_channel_id}, Expected Message ID: {rules_message_id}")

        if payload.channel_id == int(rules_channel_id) and payload.message_id == int(rules_message_id) and str(
                payload.emoji) == "📜":
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            role = guild.get_role(int(member_role_id))

            if role:
                try:
                    await member.add_roles(role)
                    #print(f"Role {role.name} assigned to {member.display_name}")
                except Exception as e:
                    pass
                    #print(f"Error assigning role: {e}")
            else:
                pass
                #print("Role not found.")
        else:
            pass
            #print("Reaction event does not match the criteria.")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        guild_id = str(guild.id)
        _, rules_channel_id, member_role_id, rules_message_id = database.get_welcome_settings(guild_id)

        # Print statements zur Überprüfung
        #print(f"Reaction removed: {payload.emoji}, Guild ID: {guild_id}, Channel ID: {payload.channel_id}, Message ID: {payload.message_id}")

        if payload.channel_id == int(rules_channel_id) and payload.message_id == int(rules_message_id) and str(
                payload.emoji) == "📜":
            member = guild.get_member(payload.user_id)
            role = guild.get_role(int(member_role_id))

            if role and member:
                try:
                    await member.remove_roles(role)
                    #print(f"Role {role.name} removed from {member.display_name}")
                except Exception as e:
                    pass
                    print(f"Error removing role: {e}")
            else:
                pass
                print("Role or member not found.")

    @commands.command(name='setupwelcome', help='Setzt den Willkommenskanal, die Rolle und den Regeltext für neue Mitglieder.')
    @commands.has_permissions(administrator=True)
    async def setup_welcome(self, ctx, welcome_channel: discord.TextChannel, rules_channel: discord.TextChannel, member_role: discord.Role, rules_message_id: int):
        guild_id = str(ctx.guild.id)
        database.set_welcome_settings(guild_id, welcome_channel.id, rules_channel.id, member_role.id, rules_message_id)
        await ctx.send(
            f"Willkommensnachrichten werden nun in {welcome_channel.mention} gesendet. Die Rolle {member_role.name} wird vergeben, wenn auf eine Nachricht (ID: {rules_message_id}) in {rules_channel.mention} reagiert wird.")


async def setup(bot):
    await bot.add_cog(welcome(bot))
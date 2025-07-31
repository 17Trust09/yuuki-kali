import discord
from discord.ext import commands
import database


class logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_or_create_user_log_channel(self, member):
        guild_id = str(member.guild.id)
        log_settings = database.get_log_settings(guild_id)
        if not log_settings:
            return None

        log_category_id, mod_role_id, admin_role_id = log_settings

        if not log_category_id:
            return None

        sanitized_name = f"{member.display_name.replace(' ', '-').lower()}-log-{member.id}"
        log_channel = discord.utils.get(member.guild.text_channels, name=sanitized_name)
        if not log_channel:
            overwrites = {
                member.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                member: discord.PermissionOverwrite(read_messages=False, send_messages=False)
            }

            mod_role = discord.utils.get(member.guild.roles, id=int(mod_role_id))
            if mod_role:
                overwrites[mod_role] = discord.PermissionOverwrite(read_messages=True)

            admin_role = discord.utils.get(member.guild.roles, id=int(admin_role_id))
            if admin_role:
                overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True)

            category = discord.utils.get(member.guild.categories, id=int(log_category_id))
            if not category:
                return None

            try:
                log_channel = await member.guild.create_text_channel(sanitized_name, overwrites=overwrites,
                                                                     category=category)
            except Exception as e:
                return None

        return log_channel

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = await self.get_or_create_user_log_channel(member)
        if channel:
            embed = discord.Embed(title="Mitglied beigetreten", description=f"{member.name} hat den Server betreten.",
                                  color=discord.Color.green())
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = await self.get_or_create_user_log_channel(member)
        if channel:
            embed = discord.Embed(title="Mitglied verlassen", description=f"{member.name} hat den Server verlassen.",
                                  color=discord.Color.red())
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild or message.author.bot:
            return
        channel = await self.get_or_create_user_log_channel(message.author)
        if channel:
            embed = discord.Embed(title="Nachricht gelöscht",
                                  description=f"Nachricht von {message.author.name} wurde gelöscht:\n{message.content}",
                                  color=discord.Color.orange())
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not before.guild or before.author.bot:
            return
        if before.content != after.content:
            channel = await self.get_or_create_user_log_channel(before.author)
            if channel:
                # Kürzen der Nachrichteninhalte auf maximal 1024 Zeichen
                before_content = (before.content[:1021] + '...') if len(before.content) > 1024 else before.content
                after_content = (after.content[:1021] + '...') if len(after.content) > 1024 else after.content

                embed = discord.Embed(title="Nachricht geändert",
                                      description=f"Nachricht von {before.author.name} wurde geändert.",
                                      color=discord.Color.blue())
                embed.add_field(name="Vorher", value=before_content, inline=False)
                embed.add_field(name="Nachher", value=after_content, inline=False)
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles or before.nick != after.nick:
            channel = await self.get_or_create_user_log_channel(before)
            if channel:
                if before.nick != after.nick:
                    embed = discord.Embed(title="Nickname geändert",
                                          description=f"{before.name} hat den Nickname geändert.",
                                          color=discord.Color.purple())
                    embed.add_field(name="Vorher", value=before.nick or before.name, inline=True)
                    embed.add_field(name="Nachher", value=after.nick or after.name, inline=True)
                    await channel.send(embed=embed)

                added_roles = [role for role in after.roles if role not in before.roles]
                removed_roles = [role for role in before.roles if role not in after.roles]
                if added_roles:
                    embed = discord.Embed(title="Rollen hinzugefügt",
                                          description=f"{after.name} hat die Rolle(n) hinzugefügt: {', '.join([role.name for role in added_roles])}",
                                          color=discord.Color.green())
                    await channel.send(embed=embed)
                if removed_roles:
                    embed = discord.Embed(title="Rollen entfernt",
                                          description=f"{after.name} hat die Rolle(n) entfernt: {', '.join([role.name for role in removed_roles])}",
                                          color=discord.Color.red())
                    await channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlogsettings(self, ctx, category: discord.CategoryChannel, mod_role: discord.Role,
                             admin_role: discord.Role):
        """Setzt die Einstellungen für das Loggen auf diesem Server."""
        database.set_log_settings(str(ctx.guild.id), str(category.id), str(mod_role.id), str(admin_role.id))
        await ctx.send(
            f"Log-Einstellungen aktualisiert: Kategorie-ID {category.id}, Mod-Rolle {mod_role.name}, Admin-Rolle {admin_role.name}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create_user_log_channel(self, ctx, member: discord.Member):
        """Erstellt manuell einen User-Log-Kanal für ein Mitglied."""
        channel = await self.get_or_create_user_log_channel(member)
        if channel:
            await ctx.send(f"User-Log-Kanal für {member.name} wurde erstellt: {channel.mention}")
        else:
            await ctx.send(f"Fehler: Log-Einstellungen sind nicht gesetzt oder Kanal konnte nicht erstellt werden.")


async def setup(bot):
    await bot.add_cog(logs(bot))

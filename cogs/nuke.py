import discord
from discord.ext import commands
import random
import asyncio
import database

class nuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def confirm(self, ctx, prompt):
        """Fragt den Benutzer nach einer Bestätigung."""
        code = random.randint(1000, 9999)
        await ctx.send(f"{prompt}\nGeben Sie den folgenden Code ein, um fortzufahren: `{code}`")
        try:
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30)
            return msg.content == str(code)
        except asyncio.TimeoutError:
            return False

    async def get_excluded_settings(self, guild_id):
        excluded_channels, excluded_categories, excluded_roles = database.get_nuke_settings(guild_id)
        return set(excluded_channels), set(excluded_categories), set(excluded_roles)

    # Die folgenden Befehle wurden entsprechend angepasst, um die Einstellungen aus der Datenbank zu nutzen:

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setnukeconfig(self, ctx, excluded_channels: str, excluded_categories: str, excluded_roles: str):
        """Setzt die Nuke-Konfiguration für den Server."""
        excluded_channel_ids = [int(id.strip()) for id in excluded_channels.split(",")]
        excluded_category_ids = [int(id.strip()) for id in excluded_categories.split(",")]
        excluded_role_ids = [int(id.strip()) for id in excluded_roles.split(",")]

        database.set_nuke_settings(str(ctx.guild.id), excluded_channel_ids, excluded_category_ids, excluded_role_ids)
        await ctx.send("Nuke-Konfiguration für den Server aktualisiert.")

    # Beispiel für einen angepassten Befehl:

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def nuke_channels(self, ctx):
        """Löscht alle Kanäle und Kategorien im Server, außer den ausgeschlossenen."""
        if not await self.confirm(ctx, "Möchten Sie wirklich alle Kanäle und Kategorien löschen?"):
            await ctx.send("Aktion abgebrochen.")
            return

        excluded_channels, excluded_categories, _ = await self.get_excluded_settings(str(ctx.guild.id))

        for channel in ctx.guild.channels:
            if channel.id not in excluded_channels and (not isinstance(channel, discord.CategoryChannel) or channel.id not in excluded_categories):
                await channel.delete()

        start_channel = await ctx.guild.create_text_channel("Start")
        await start_channel.send("Alle Kanäle und Kategorien wurden gelöscht!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def nuke_channels(self, ctx):
        """Löscht alle Kanäle und Kategorien im Server, außer den ausgeschlossenen."""
        if not await self.confirm(ctx, "Möchten Sie wirklich alle Kanäle und Kategorien löschen?"):
            await ctx.send("Aktion abgebrochen.")
            return

        excluded_channels, excluded_categories, _ = await self.get_excluded_settings(str(ctx.guild.id))

        for channel in ctx.guild.channels:
            if channel.id not in excluded_channels and (
                    not isinstance(channel, discord.CategoryChannel) or channel.id not in excluded_categories):
                await channel.delete()

        start_channel = await ctx.guild.create_text_channel("Start")
        await start_channel.send("Alle Kanäle und Kategorien wurden gelöscht!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def nuke_messages(self, ctx):
        """Löscht alle Nachrichten in allen Kanälen, außer den ausgeschlossenen Kanälen."""
        if not await self.confirm(ctx,
                                  "Möchten Sie wirklich alle Nachrichten löschen, außer in den ausgeschlossenen Kanälen?"):
            await ctx.send("Aktion abgebrochen.")
            return

        excluded_channels, excluded_categories, _ = await self.get_excluded_settings(str(ctx.guild.id))

        for channel in ctx.guild.text_channels:
            if channel.id not in excluded_channels and channel.category_id not in excluded_categories:
                await channel.purge(limit=None)
        await ctx.send("Alle Nachrichten wurden gelöscht!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def nuke_all(self, ctx):
        """Löscht alle Kanäle, Kategorien und Rollen im Server."""
        if not await self.confirm(ctx, "Möchten Sie wirklich alle Kanäle, Kategorien und Rollen löschen?"):
            await ctx.send("Aktion abgebrochen.")
            return

        excluded_channels, excluded_categories, excluded_roles = await self.get_excluded_settings(str(ctx.guild.id))

        # Löschen von Kanälen und Kategorien
        for channel in ctx.guild.channels:
            if channel.id not in excluded_channels and (
                    not isinstance(channel, discord.CategoryChannel) or channel.id not in excluded_categories):
                try:
                    await channel.delete()
                except discord.Forbidden:
                    await ctx.send(f"Keine Berechtigung, um den Kanal {channel.name} zu löschen.")
                except discord.HTTPException:
                    await ctx.send(f"Fehler beim Löschen des Kanals {channel.name}.")

        # Löschen von Rollen
        for role in ctx.guild.roles:
            if role.id not in excluded_roles and role != ctx.guild.default_role and not role.managed:
                try:
                    await role.delete()
                except discord.Forbidden:
                    await ctx.send(f"Keine Berechtigung, um die Rolle {role.name} zu löschen.")
                except discord.HTTPException:
                    await ctx.send(f"Fehler beim Löschen der Rolle {role.name}.")

        # Erstellen eines "Start"-Kanals und Posten einer Nachricht
        start_channel = await ctx.guild.create_text_channel("Start")
        await start_channel.send("Alle Kanäle, Kategorien und Rollen wurden gelöscht!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def nuke_roles(self, ctx):
        """Löscht alle Rollen im Server, außer den ausgeschlossenen Rollen."""
        if not await self.confirm(ctx, "Möchten Sie wirklich alle Rollen löschen?"):
            await ctx.send("Aktion abgebrochen.")
            return

        excluded_channels, excluded_categories, excluded_roles = await self.get_excluded_settings(str(ctx.guild.id))

        for role in ctx.guild.roles:
            if role.id not in excluded_roles and role != ctx.guild.default_role and not role.managed:
                try:
                    await role.delete()
                except discord.Forbidden:
                    await ctx.send(f"Keine Berechtigung, um die Rolle {role.name} zu löschen.")
                except discord.HTTPException:
                    await ctx.send(f"Fehler beim Löschen der Rolle {role.name}.")
        await ctx.send("Alle Rollen wurden gelöscht!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def joke_nuke(self, ctx):
        main_chat = discord.utils.get(ctx.guild.text_channels, name="💬main-chat")
        if not main_chat:
            await ctx.send("💬main-chat konnte nicht gefunden werden!")
            return

        embed = discord.Embed(
            title="⚠️ ACHTUNG! ⚠️",
            description="Wenn du auf den Knopf unten drückst, wird der Server gelöscht. Nutzen auf eigenes Risiko und keiner außer dir übernimmt die Haftung!",
            color=discord.Color.red()
        )
        message = await main_chat.send(embed=embed)
        await message.add_reaction("💥")

        def check_reaction(reaction, user):
            return user != self.bot.user and str(reaction.emoji) == "💥" and reaction.message.id == message.id

        try:
            reaction, reactor = await self.bot.wait_for('reaction_add', timeout=3600,
                                                        check=check_reaction)  # Warte 1 Stunde
        except asyncio.TimeoutError:
            await message.delete()
        else:
            await message.remove_reaction("💥", reactor)
            code = random.randint(1000, 9999)  # Generiere einen zufälligen 4-stelligen Code
            confirm_message = await main_chat.send(
                f"{reactor.mention}, gib den folgenden Code ein, um zu bestätigen: `{code}`\n"
                "Oder schreibe 'abbrechen' um den Vorgang abzubrechen.")

            def code_check(m):
                return m.author == reactor and (m.content == str(code) or m.content.lower() == "abbrechen")

            try:
                response = await self.bot.wait_for('message', timeout=60,
                                                   check=code_check)  # Warte 1 Minute auf den Code oder die Abbruchnachricht
                if response.content.lower() == "abbrechen":
                    await main_chat.send(f"{reactor.mention} hat den Vorgang abgebrochen.")
                    return
            except asyncio.TimeoutError:
                await main_chat.send(f"{reactor.mention} hat den Vorgang abgebrochen.")
            else:
                countdown_message = await main_chat.send(
                    f"Achtung! {reactor.mention} hat den Knopf gedrückt! Serverlöschung in 10 Sekunden!")
                for i in range(9, 0, -1):
                    await asyncio.sleep(1)
                    await countdown_message.edit(
                        content=f"Achtung! {reactor.mention} hat den Knopf gedrückt! Serverlöschung in {i} Sekunden!")

                # Fügen Sie hier eine humorvolle oder harmlose Aktion hinzu
                await main_chat.send(f"Scherzalarm! Keine Panik, {reactor.mention}. Der Server ist sicher.")

                # Lösche die Nachrichten des Bots und des Benutzers
                await countdown_message.delete()
                await message.delete()
                await confirm_message.delete()
                await response.delete()


async def setup(bot):
    await bot.add_cog(nuke(bot))

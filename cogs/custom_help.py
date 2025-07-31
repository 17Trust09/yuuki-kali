import discord
from discord.ext import commands

class custom_help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setup_help")
    async def custom_help(self, ctx):
        """Zeigt eine Liste aller verfügbaren Befehle und ihre Beschreibungen an."""
        # Liste der Befehle, die du im ersten Embed anzeigen möchtest
        command_list1 = [
            ("Setze das Prefix für deinen Server", "!setprefix <prefix>"),
            ("Cog Managment alle anzeigen", "!list_cogs"),
            ("Cog Managment Cogs laden", "!toggle_cog <cog_name>"),
            ("Nötige Cogs", "welcome ; tickets ; twitch_live_checker ; bot_status_cog ; antispam ; feedback ; logs"),
            ("Setup für Willkommens Nachricht und Member Rolle", "!setupwelcome <welcome_channel> <rules_channel> <member_role> <rules_message_id>"),
            ("TicketSystem - Erstellung der Ticket Nachricht", "!create_ticket_message"),
            ("TicketSystem - Setup des Ticketsystems", "!set_ticket_message <message_id>"),
            ("Setup Stream Announcments und Streamer", "!setlivestream <channel> <streamer_names>"),
            ("Setup des Bot Status", "!set_streamer <streamer_name>"),
            ("Setup der Anti Spam Regelung", "!setspamsettings <message_limit> <time_limit>"),
            ("Setup der Anti Spam Regelung", "!setup_leveling <message_limit> <time_limit>"),
            ("Setup Level Channel", "!setlogsettings <LogCategory> <ModeratorRole> <AdminRole>"),
            ("Setup des Server Stats", "!setupstats Twitch:<TwitchName>"),
            ("Setup des Server Stats", "!setupstats YouTube:<YouTubeID>"),
            ("Setup des Server Stats", "!setupstats Twitter:<TwitterName>"),
            ("Setup des Server Stats", "!setupstats Instagram:<BenutzerID>")
        ]

        # Erstelle das erste Embed
        embed1 = discord.Embed(title="Server Setup Liste", color=discord.Color.blue())
        for name, value in command_list1:
            embed1.add_field(name=name, value=value, inline=False)

        # Sende beide Embeds
        await ctx.send(embed=embed1)

async def setup(bot):
    await bot.add_cog(custom_help(bot))
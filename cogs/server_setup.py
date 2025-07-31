import discord
from discord.ext import commands

class server_setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def setup_server(self, ctx):
        # Kategorien und Kanäle erstellen
        categories = {
            "📊 SERVER STATS 📊": ["Twitch Follower", "Total Member", "Online Member", "Bots"],
            "SERVER INFO": ["👋Eingangshalle", "📜Regeln", "💠Announcements", "🎉Giveaways", "💻Social Media", "📰Werbung"],
            "CHAT MIT ANDEREN": ["💬Main Chat", "😂Mems und shitpost", "🎮Game Ideen", "📷Picture share", "🚨nsfw", "🎥Stream Clips", "Links und mehr"],
            "SUPPORTER AREA": ["Allgemein", "Supporter Lounge", "Supporter Room"],
            "SPECIAL AREA": ["💎Allgemein", "📜Feedback", "💎Special Lounge | 1", "💎Special Lounge | 2"],
            "SPRACH CHANNELS": ["🌏Chat | 1", "🌏Chat | 2"],
            "PLAYING AREA": ["Looking for Game", "Stream | 1", "Stream | 2", "Waiting Room", "Gaming Room", "Gaming Room | 1", "Gaming Room | 2", "Gaming Room | 3", "Gaming Room | 4", "Gaming Room | 5", "AFK-Room"],
            "STAFF": ["Allgemein stuff Talk", "Ideen und Tipps", "❗ToDo", "Server Info Management", "Mod log", "Staff Lounge", "Server Bans:"],
            "USER LOG": []
        }

        for category_name, channels in categories.items():
            category = await ctx.guild.create_category(category_name)
            for channel_name in channels:
                if channel_name == "💬Main Chat":
                    await ctx.guild.create_text_channel(channel_name, category=category)
                elif any(voice_indicator in channel_name for voice_indicator in ["|", "Lounge", "Room", "Chat"]):
                    await ctx.guild.create_voice_channel(channel_name, category=category)
                else:
                    await ctx.guild.create_text_channel(channel_name, category=category)

        # Rollen mit Farben erstellen
        roles_with_colors = {
            "Owner": discord.Color.red(),
            "Bot": discord.Color.greyple(),
            "--🎥Live🎥--": discord.Color.dark_purple(),
            "--------Staff--------": discord.Color.greyple(),
            "Streamer": discord.Color.purple(),
            "⚙️Management": discord.Color.dark_purple(),
            "Secretary": discord.Color.dark_red(),
            "Co-Owner": discord.Color.red(),
            "Admin": discord.Color.orange(),
            "--------Modorator Rollen--------": discord.Color.greyple(),
            "Mod": discord.Color.green(),
            "--------Server Member--------": discord.Color.greyple(),
            "Mute": discord.Color.red(),
            "VIP": discord.Color.gold(),
            "Server Booster": discord.Color.gold(),
            "Youtuber": discord.Color.dark_magenta(),
            "Friend": discord.Color.dark_green(),
            "Member": discord.Color.orange(),
            "Gast": discord.Color.blue(),
            "--------NoName--------": discord.Color.greyple(),
            "Stream Info": discord.Color.greyple()
        }

        for role_name, role_color in roles_with_colors.items():
            await ctx.guild.create_role(name=role_name, color=role_color)

        # Löschen des "Start"-Kanals
        start_channel = discord.utils.get(ctx.guild.channels, name="start")
        if start_channel:
            await ctx.send("Start-Kanal gefunden.")  # Logging
            bot_member = ctx.guild.get_member(self.bot.user.id)
            if start_channel.permissions_for(bot_member).manage_channels:
                await ctx.send("Berechtigung zum Löschen des Kanals vorhanden.")  # Logging
                await start_channel.delete()
            else:
                await ctx.send("Keine Berechtigung zum Löschen des Start-Kanals.")
        else:
            await ctx.send("Start-Kanal wurde nicht gefunden.")

        # Nachricht in 📜regeln posten und mit ✅ reagieren
        rules_channel = discord.utils.get(ctx.guild.text_channels, name="📜regeln")
        if rules_channel:
            #await ctx.send("📜regeln Kanal gefunden.")  # Logging
            bot_member = ctx.guild.get_member(self.bot.user.id)
            if rules_channel.permissions_for(bot_member).send_messages:
                #await ctx.send("Berechtigung zum Senden von Nachrichten vorhanden.")  # Logging
                if rules_channel.permissions_for(bot_member).add_reactions:
                    #await ctx.send("Berechtigung zum Hinzufügen von Reaktionen vorhanden.")  # Logging
                    message = await rules_channel.send(
                        "Bitte lies dir die Regeln durch und bestätige diese indem du drauf reagierst :regeln:. Danach bekommst du vollen Zugang zum Server. Eröffne bitte ein Ticket, wenn dieses nicht funktionieren sollte."
                        "\n\n#1. Behandle alle mit Respekt. Belästigung, Hexenjagd, Sexismus, Rassismus oder Volksverhetzung werden absolut nicht toleriert. Rassismus, Volksverhetzung oder böswilliges \"Hinter'm-Rücken-Gerede\" bzgl. Admins, Mods und anderen Mitgliedern werden absolut nicht toleriert."
                        "\n\n#2. Avatare, Nicknamen und Beschreibungen dürfen keine pornographischen, rassistischen oder beleidigenden Inhalte beinhalten."
                        "\n\n#3. Keine NSFW- oder obszönen Inhalte (Außer in den vorgesehenen 🚨nsfw channel). Dazu zählen Texte, Bilder oder Links mit Nacktheit, Sex, schwerer Gewalt oder anderen grafisch verstörenden Inhalten."
                        "\n\n#4. Wer den Anweisungen des Server-Admins bzw. der Supporter nicht folgt wird verwarnt und im Ernstfall gekickt. Sollte sich dies häufen, ist ein Bann zu erwarten."
                        "\n\n#5. Das hinter dem Rücken Gerede gegenüber Admins und allen anderen Mitgliedern hier im Discord wie z.B. wegen einer Behinderung oder sonstigen Dingen ist strengstens untersagt da dies Verletzung der Privatsphäre ist."
                        "\n\n#6. Es sind alle Nutzer angehalten, die Discord-Server regeln zu beachten. Wenn du etwas sieht, das gegen die Regeln verstößt, oder wodurch du dich nicht sicher fühlst, dann benachrichtige die Mitarbeiter. Wir möchten, dass dieser Server ein Ort ist, an dem sich jeder willkommen fühlt."
                        "\n\n#7. Admin und Mod Rechte werden nicht wahllos und nur an vertrauenswürdige User vergeben."
                        "\n\n#8. Administratoren behalten sich das Recht auf einen dauerhaften Bann vor!"
                    )
                    await message.add_reaction("✅")

                # Nachricht in "👋eingangshalle" posten
                entrance_channel = discord.utils.get(ctx.guild.text_channels, name="👋eingangshalle")
                if entrance_channel:
                    await entrance_channel.send("Server-Setup abgeschlossen! Nutze !create_ticket_message um Die Info im Support channel zu posten")



async def setup(bot):
    await bot.add_cog(server_setup(bot))

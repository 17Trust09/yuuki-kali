from discord.ext import commands, tasks
import discord
import database
import requests
import tweepy
from googleapiclient.discovery import build
# Ihre API-Schlüssel
twitch_client_id = 'tba4vhbrcseokqhlimy7jkjgri18wh'
twitch_client_secret = 'dnwvlg0opxyon3dxv6new2018egpi7'
twitter_consumer_key = 'IHR_TWITTER_CONSUMER_KEY'
twitter_consumer_secret = 'IHR_TWITTER_CONSUMER_SECRET'
twitter_access_token = 'IHR_TWITTER_ACCESS_TOKEN'
twitter_access_token_secret = 'IHR_TWITTER_ACCESS_TOKEN_SECRET'
instagram_access_token = 'IHR_INSTAGRAM_ACCESS_TOKEN'
instagram_user_id = 'IHR_INSTAGRAM_USER_ID'
youtube_api_key = 'IHR_YOUTUBE_API_KEY'




class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_stats.start()


    async def setup_stats_channels(self, guild, platforms):
        """
        Erstellt eine Kategorie und zugehörige Kanäle für die Serverstatistiken.

        :param guild: Die Discord-Gilde (Server), für die die Kanäle eingerichtet werden sollen.
        :param platforms: Eine Liste von Plattformnamen, für die Kanäle erstellt werden sollen.
        """
        # Überprüfen, ob die Kategorie bereits existiert
        stats_category = discord.utils.get(guild.categories, name="📊 SERVER STATS 📊")
        if not stats_category:
            stats_category = await guild.create_category("📊 SERVER STATS 📊")

        # Erstellen der erforderlichen Kanäle für jede Plattform
        for platform in platforms:
            channel_name = f"{platform} Follower:"
            existing_channel = discord.utils.get(stats_category.channels, name=channel_name)
            if not existing_channel:
                await guild.create_voice_channel(channel_name, category=stats_category)

    @commands.command(name='setupstats', help='Richtet die Serverstatistiken ein.')
    @commands.has_permissions(administrator=True)
    async def setup_stats(self, ctx, *args):
        """
        Ein Command, um die Serverstatistik-Kanäle und Plattform-Identifikatoren einzurichten.

        :param ctx: Der Kontext, in dem der Befehl ausgeführt wird.
        :param args: Eine Liste von Argumenten im Format 'Plattform:Benutzername/ID'.
        """
        if not args:
            await ctx.send(
                "Bitte gib mindestens eine Plattform und einen Benutzernamen/ID im Format 'Plattform:Benutzername' an.")
            return

        platforms = []
        for arg in args:
            try:
                platform, identifier = arg.split(':')
                platforms.append(platform)
                database.set_platform_identifier(ctx.guild.id, platform, identifier)
            except ValueError:
                await ctx.send(f"Fehlerhaftes Format: '{arg}'. Erwartetes Format: 'Plattform:Benutzername'")
                return

        # Einrichten der Statistik-Kanäle für die angegebenen Plattformen
        await self.setup_stats_channels(ctx.guild, platforms)
        await ctx.send(f"Serverstatistiken eingerichtet für Plattformen: {', '.join(platforms)}")


    def get_platform_followers(self, guild_id, platform, identifier):
        """
        Ruft die Follower-Anzahl für eine bestimmte Plattform ab.

        :param guild_id: Die ID des Discord-Servers.
        :param platform: Der Name der Plattform (z.B. "Twitch", "YouTube", "Twitter", "Instagram").
        :param identifier: Der Benutzername oder die ID für die Plattform.
        :return: Die Anzahl der Follower oder None, falls ein Fehler auftritt.
        """
        if platform == "Twitch":
            return self.get_twitch_followers(identifier)
        elif platform == "YouTube":
            return self.get_youtube_subscribers(identifier)
        elif platform == "Twitter":
            return self.get_twitter_followers(identifier)
        elif platform == "Instagram":
            return self.get_instagram_followers(identifier)
        else:
            print(f"Unbekannte Plattform: {platform}")
            return None


    def get_twitter_followers(self, api_keys, username):
        """
        Ruft die Anzahl der Follower für einen Twitter-Benutzer ab.

        :param api_keys: Ein Dictionary mit den Twitter API-Schlüsseln ('consumer_key', 'consumer_secret', 'access_token', 'access_token_secret').
        :param username: Der Benutzername des Twitter-Benutzers.
        :return: Die Anzahl der Follower oder None, falls ein Fehler auftritt.
        """
        auth = tweepy.OAuthHandler(api_keys['consumer_key'], api_keys['consumer_secret'])
        auth.set_access_token(api_keys['access_token'], api_keys['access_token_secret'])
        api = tweepy.API(auth)

        try:
            user = api.get_user(screen_name=username)
            return user.followers_count
        except tweepy.TweepError as e:
            print(f"Fehler beim Abrufen der Twitter-Daten: {e}")
            return None

    def get_youtube_subscribers(self, api_key, channel_id):
        """
        Ruft die Anzahl der Abonnenten für einen YouTube-Kanal ab.

        :param api_key: Der YouTube Data API-Schlüssel.
        :param channel_id: Die ID des YouTube-Kanals.
        :return: Die Anzahl der Abonnenten oder None, falls ein Fehler auftritt.
        """
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.channels().list(
            part="statistics",
            id=channel_id
        )
        response = request.execute()

        if 'items' in response and response['items']:
            return int(response['items'][0]['statistics']['subscriberCount'])
        else:
            print("Keine Daten für den angegebenen YouTube-Kanal gefunden.")
            return None

    def get_instagram_followers(self, api_keys):
        """
        Ruft die Anzahl der Follower für ein Instagram-Konto ab.

        :param api_keys: Ein Dictionary mit dem Zugriffstoken und der Benutzer-ID für die Instagram Graph API.
        :return: Die Anzahl der Follower oder None, falls ein Fehler auftritt.
        """
        access_token = api_keys['access_token']
        instagram_user_id = api_keys['user_id']
        url = f"https://graph.instagram.com/{instagram_user_id}?fields=followers_count&access_token={access_token}"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("followers_count")
        else:
            print(f"Fehler beim Abrufen der Instagram-Daten: {response.status_code}")
            return None

    def get_twitch_followers(self, api_keys, username):
        """
        Ruft die Anzahl der Follower für einen Twitch-Kanal ab.

        :param api_keys: Ein Dictionary mit der Client-ID und dem Client-Secret für die Twitch API.
        :param username: Der Benutzername des Twitch-Kanals.
        :return: Die Anzahl der Follower oder None, falls ein Fehler auftritt.
        """
        client_id = api_keys['client_id']
        client_secret = api_keys['client_secret']

        # OAuth-Token von Twitch anfordern
        url = 'https://id.twitch.tv/oauth2/token'
        params = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'
        }
        response = requests.post(url, params=params)
        data = response.json()
        token = data.get('access_token')

        if not token:
            print("Fehler beim Abrufen des OAuth-Tokens von Twitch.")
            return None

        # Twitch API-Anfrage, um Follower-Daten zu erhalten
        headers = {
            'Client-ID': client_id,
            'Authorization': f'Bearer {token}'
        }
        url = f'https://api.twitch.tv/helix/users?login={username}'
        response = requests.get(url, headers=headers)
        user_data = response.json()

        if user_data.get('data'):
            user_id = user_data['data'][0]['id']
            url = f'https://api.twitch.tv/helix/users/follows?to_id={user_id}'
            response = requests.get(url, headers=headers)
            follower_data = response.json()
            return follower_data.get('total', 0)

        print(f"Fehler beim Abrufen der Twitch-Daten für Benutzer {username}.")
        return None

    @tasks.loop(minutes=5)
    async def update_stats(self):
        for guild in self.bot.guilds:
            # Abrufen der Plattformen und API-Schlüssel für den jeweiligen Server
            platforms = database.get_platforms(guild.id)
            api_keys = database.get_api_keys(guild.id)

            # Überprüfen der Kategorie "📊 SERVER STATS 📊" und Aktualisieren der Kanäle
            stats_category = discord.utils.get(guild.categories, name="📊 SERVER STATS 📊")
            if stats_category:
                for platform in platforms:
                    # Abrufen der Follower-Zahlen basierend auf der Plattform
                    follower_count = self.get_platform_followers(guild.id, platform, api_keys)

                    # Aktualisieren des entsprechenden Kanals
                    channel_name = f"{platform} Follower:"
                    channel = discord.utils.get(stats_category.channels, name=channel_name)
                    if channel and follower_count is not None:
                        await channel.edit(name=f"{channel_name} {follower_count}")



    @update_stats.before_loop
    async def before_update_stats(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(ServerStats(bot))
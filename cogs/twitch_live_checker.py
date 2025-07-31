import discord
from discord.ext import commands, tasks
import requests
import database
import time
import json
import os

class TwitchLiveChecker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.CLIENT_ID = 'tba4vhbrcseokqhlimy7jkjgri18wh'
        self.CLIENT_SECRET = 'dnwvlg0opxyon3dxv6new2018egpi7'
        self.oauth_token = self.get_oauth_token()
        self.live_streamers = set()  # Re-added live_streamers set

        self.known_streams_file = "known_streams.json"
        self.known_streams = self.load_known_streams()

        self.check_live_status.start()
        self.renew_token.start()

    def get_oauth_token(self):
        url = 'https://id.twitch.tv/oauth2/token'
        params = {
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
            'grant_type': 'client_credentials'
        }
        response = requests.post(url, params=params)
        data = response.json()
        return data['access_token']

    def load_known_streams(self):
        if not os.path.exists(self.known_streams_file):
            with open(self.known_streams_file, "w") as f:
                json.dump({}, f)
        with open(self.known_streams_file, "r") as f:
            return json.load(f)

    def save_known_streams(self):
        with open(self.known_streams_file, "w") as f:
            json.dump(self.known_streams, f)

    @tasks.loop(minutes=50)
    async def renew_token(self):
        self.oauth_token = self.get_oauth_token()
        print("OAuth token renewed!")

    @tasks.loop(minutes=5)
    async def check_live_status(self):
        headers = {
            'Client-ID': self.CLIENT_ID,
            'Authorization': f'Bearer {self.oauth_token}'
        }

        active_streams = {}  # streamer: stream_id

        for guild in self.bot.guilds:
            channel_id, streamer_list = database.get_live_checker_settings(str(guild.id))
            if not channel_id or not streamer_list:
                continue

            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                continue

            streamers = streamer_list.split(',')
            for streamer in streamers:
                response = requests.get(f'https://api.twitch.tv/helix/streams?user_login={streamer}', headers=headers)

                if response.status_code == 200:
                    data = response.json()

                    if data.get('data'):
                        stream = data['data'][0]
                        stream_id = stream['id']
                        active_streams[streamer] = stream_id

                        user_response = requests.get(f'https://api.twitch.tv/helix/users?login={streamer}', headers=headers)
                        user_data = user_response.json()
                        user_info = user_data['data'][0]

                        if self.known_streams.get(streamer) != stream_id:
                            thumbnail_url = stream['thumbnail_url'].format(width=1920, height=1080)
                            thumbnail_url += f"?t={int(time.time())}"

                            embed = discord.Embed(
                                title=f"{stream['user_name']} ist jetzt live auf Twitch!",
                                url=f"https://twitch.tv/{stream['user_name']}",
                                description=stream['title'],
                                color=discord.Color.purple()
                            )
                            embed.set_author(name=stream['user_name'], icon_url=user_info['profile_image_url'])
                            embed.set_image(url=thumbnail_url)
                            embed.add_field(name="Spiel", value=stream['game_name'], inline=True)
                            embed.add_field(name="Zuschauer", value=stream['viewer_count'], inline=True)
                            embed.set_footer(text="Live auf Twitch")

                            await channel.send(content="@everyone", embed=embed)
                            self.known_streams[streamer] = stream_id

                else:
                    print(f"Error fetching data for {streamer}: {response.status_code}, Response: {response.text}")

        # Bereinige bekannte Streams, die nicht mehr aktiv sind
        cleaned = False
        for streamer in list(self.known_streams.keys()):
            if streamer not in active_streams:
                del self.known_streams[streamer]
                cleaned = True

        if cleaned or self.known_streams != active_streams:
            self.save_known_streams()

    @commands.command(name="setlivestream")
    @commands.has_permissions(administrator=True)
    async def set_live_stream(self, ctx, channel: discord.TextChannel, *, streamer_names: str):
        streamers = streamer_names.split(',')
        database.set_live_checker_settings(str(ctx.guild.id), str(channel.id), streamers)
        await ctx.send(f"Live-Benachrichtigungen werden im Kanal {channel.mention} für Streamer {', '.join(streamers)} gesendet.")

    @check_live_status.before_loop
    async def before_check_live_status(self):
        await self.bot.wait_until_ready()

    @renew_token.before_loop
    async def before_renew_token(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.check_live_status.cancel()
        self.renew_token.cancel()

async def setup(bot):
    await bot.add_cog(TwitchLiveChecker(bot))

import discord
from discord.ext import commands, tasks
import requests
import database  # Stellen Sie sicher, dass die database.py im gleichen Verzeichnis liegt

class bot_status_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_status = discord.Game("am Code")  # Standard-Status
        self.oauth_token = self.get_oauth_token()
        self.check_streamer_status.start()

    def get_oauth_token(self):
        client_id = 'tba4vhbrcseokqhlimy7jkjgri18wh'
        client_secret = 'dnwvlg0opxyon3dxv6new2018egpi7'
        url = 'https://id.twitch.tv/oauth2/token'

        params = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'
        }

        response = requests.post(url, params=params)
        data = response.json()
        return data['access_token']

    @tasks.loop(minutes=5)
    async def check_streamer_status(self):
        for guild in self.bot.guilds:
            guild_id = str(guild.id)
            streamer_name = database.get_streamer_settings(guild_id)[0]

            if not streamer_name:
                await self.bot.change_presence(activity=self.default_status)
                continue

            headers = {
                "Client-ID": "tba4vhbrcseokqhlimy7jkjgri18wh",
                'Authorization': f'Bearer {self.oauth_token}'
            }

            try:
                response = requests.get(f"https://api.twitch.tv/helix/streams?user_login={streamer_name}", headers=headers)
                data = response.json()

                if "data" in data and data["data"]:  # Wenn der Streamer live ist
                    stream_url = f"https://twitch.tv/{streamer_name}"
                    await self.bot.change_presence(
                        activity=discord.Streaming(name=f"streamt {streamer_name}", url=stream_url))
                else:  # Wenn der Streamer offline ist
                    await self.bot.change_presence(activity=self.default_status)
            except Exception as e:
                print(f"Error fetching data for {streamer_name}: {response.status_code}, Response: {response.text}, Error: {e}")
                await self.bot.change_presence(activity=self.default_status)

    @commands.command(name='set_streamer')
    @commands.has_permissions(administrator=True)
    async def set_streamer(self, ctx, streamer_name: str):
        """Setzt den Twitch Streamer-Namen beim Bot"""
        guild_id = str(ctx.guild.id)
        database.set_streamer_settings(guild_id, streamer_name)
        await ctx.send(f"Twitch Streamer für diesen Server wurde auf {streamer_name} gesetzt.")

async def setup(bot):
    await bot.add_cog(bot_status_cog(bot))

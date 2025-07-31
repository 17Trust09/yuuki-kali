import discord
from discord.ext import commands, tasks
import feedparser
import database

class RSSFeedManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_feeds.start()
        self.print_guilds()

    def print_guilds(self):
        print("Listing all guilds the bot is connected to:")
        for guild in self.bot.guilds:
            print(f'Connected to guild: {guild.name} (ID: {guild.id})')

    @commands.command(name="rss")
    @commands.has_permissions(administrator=True)
    async def rss_command(self, ctx):
        await ctx.send("Bitte gib die Kategorie für den RSS Feed ein:")

        def check_category(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            category_msg = await self.bot.wait_for('message', check=check_category, timeout=60)
            category_name = category_msg.content
            category = discord.utils.get(ctx.guild.categories, name=category_name)
            if not category:
                await ctx.send(f"Kategorie {category_name} nicht gefunden. Vorgang abgebrochen.")
                return

            await ctx.send("Bitte gib den Namen des neuen Kanals ein:")

            def check_channel(m):
                return m.author == ctx.author and m.channel == ctx.channel

            channel_msg = await self.bot.wait_for('message', check=check_channel, timeout=60)
            channel_name = channel_msg.content

            await ctx.send("Bitte gib die URL des RSS-Feeds ein:")

            def check_url(m):
                return m.author == ctx.author and m.channel == ctx.channel

            rss_url_msg = await self.bot.wait_for('message', check=check_url, timeout=60)
            rss_url = rss_url_msg.content

            channel = await ctx.guild.create_text_channel(channel_name, category=category)
            database.add_feed(ctx.guild.id, channel.id, rss_url)
            await ctx.send(f"RSS-Feed-Kanal {channel.mention} wurde erstellt und der RSS-Feed hinzugefügt.")

        except asyncio.TimeoutError:
            await ctx.send("Zeitüberschreitung. Vorgang abgebrochen.")

    @tasks.loop(minutes=10)
    async def check_feeds(self):
        feeds = database.get_all_feeds()
        for guild_id, channel_id, rss_url, last_entry_id in feeds:
            #print(f"Checking feed for guild {guild_id}, channel {channel_id}, url {rss_url}")

            # Convert guild_id to integer if not already
            guild_id = int(guild_id)
            channel_id = int(channel_id)

            feed = feedparser.parse(rss_url)
            if not feed.entries:
                #print(f"No entries found for feed {rss_url}")
                continue

            latest_entry = feed.entries[0]
            if latest_entry.id != last_entry_id:
                guild = self.bot.get_guild(guild_id)
                #print(f"Attempting to fetch guild with ID {guild_id}, found: {guild}")
                if guild is None:
                    #print(f"Guild with ID {guild_id} not found.")
                    continue

                channel = guild.get_channel(channel_id)
                #print(f"Attempting to fetch channel with ID {channel_id} in guild {guild_id}, found: {channel}")
                if channel is None:
                    #print(f"Channel with ID {channel_id} not found in guild {guild_id}.")
                    continue

                await channel.send(f"Neuer Eintrag: {latest_entry.title}\n{latest_entry.link}")
                database.update_feed_last_entry_id(guild_id, channel_id, rss_url, latest_entry.id)

    @check_feeds.before_loop
    async def before_check_feeds(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(RSSFeedManager(bot))

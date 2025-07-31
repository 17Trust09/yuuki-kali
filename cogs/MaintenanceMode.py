import discord
from discord.ext import commands
import asyncio
from datetime import datetime


class Maintenance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_maintenance_mode = False
        self.maintenance_start_time = None

    async def send_dm_menu(self, ctx=None):
        """Sendet eine interaktive Nachricht mit Buttons in der DM des Bot-Owners."""
        owner = await self.bot.fetch_user(530391227753955338)  # Ersetze mit deiner ID
        view = MaintenanceMenu(self)

        try:
            await owner.send("🔧 **Wartungsmodus Steuerung** 🔧\nWähle eine Aktion:", view=view)
        except discord.HTTPException:
            print("Fehler: DM an den Owner konnte nicht gesendet werden.")

    @commands.command()
    async def maintenance(self, ctx):
        """Aktiviert den Wartungsmodus und sendet eine Nachricht in allen Servern"""

        if isinstance(ctx, discord.Interaction):
            user = ctx.user  # Falls der Befehl per Button ausgeführt wird
            await ctx.response.defer()
        else:
            user = ctx.author  # Falls der Befehl per Textcommand ausgeführt wird

        if user.id != 530391227753955338:
            await ctx.send("Diese Funktion ist nur für den Bot-Besitzer verfügbar.")
            return

        self.is_maintenance_mode = True
        self.maintenance_start_time = datetime.now()

        embed = discord.Embed(
            title="⚠️ **Wartungsmodus aktiviert** ⚠️",
            description="Der Bot ist momentan im Wartungsmodus und nicht vollständig verfügbar.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Wartung seit:", value=f"{self.maintenance_start_time.strftime('%d.%m.%Y %H:%M:%S')}",
                        inline=False)
        embed.set_footer(text=f"Bot: {self.bot.user.name}")

        affected_servers = []
        for guild in self.bot.guilds:
            affected_servers.append(guild.name)
            target_channel = discord.utils.get(guild.channels, name="allgemein-stuff-talk") or \
                             discord.utils.get(guild.channels, name="general")
            if target_channel:
                await target_channel.send(embed=embed)
            await asyncio.sleep(1)

        affected_servers_text = "\\n".join(affected_servers) if affected_servers else "Keine Server gefunden."
        owner = await self.bot.fetch_user(530391227753955338)
        await owner.send(f"🔧 **Wartungsmodus aktiviert. Betroffene Server:**\\n{affected_servers_text}")

        await self.send_dm_menu()

    @commands.command()
    async def maintenance_end(self, ctx):
        """Deaktiviert den Wartungsmodus und sendet eine Nachricht in allen Servern"""

        if isinstance(ctx, discord.Interaction):
            user = ctx.user  # Falls der Befehl per Button ausgeführt wird
            await ctx.response.defer()
        else:
            user = ctx.author  # Falls der Befehl per Textcommand ausgeführt wird

        if user.id != 530391227753955338:
            await ctx.send("Diese Funktion ist nur für den Bot-Besitzer verfügbar.")
            return

        self.is_maintenance_mode = False

        embed = discord.Embed(
            title="✅ **Wartungsmodus beendet** ✅",
            description="Der Bot ist wieder vollständig verfügbar.",
            color=discord.Color.green()
        )
        embed.add_field(name="Wiederherstellung:", value=f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
                        inline=False)
        embed.set_footer(text=f"Bot: {self.bot.user.name}")

        affected_servers = []
        for guild in self.bot.guilds:
            affected_servers.append(guild.name)
            target_channel = discord.utils.get(guild.channels, name="allgemein-stuff-talk") or \
                             discord.utils.get(guild.channels, name="general")
            if target_channel:
                await target_channel.send(embed=embed)
            await asyncio.sleep(1)

        affected_servers_text = "\\n".join(affected_servers) if affected_servers else "Keine Server gefunden."
        owner = await self.bot.fetch_user(530391227753955338)
        await owner.send(f"✅ **Wartungsmodus beendet. Betroffene Server:**\\n{affected_servers_text}")

        await self.send_dm_menu(ctx if isinstance(ctx, commands.Context) else None)

    @commands.command()
    async def status(self, ctx):
        """Gibt den aktuellen Status des Bots zurück."""
        if self.is_maintenance_mode:
            uptime = datetime.now() - self.maintenance_start_time
            embed = discord.Embed(
                title="🔧 **Wartungsmodus aktiv** 🔧",
                description=f"Der Bot ist seit {uptime} im Wartungsmodus.",
                color=discord.Color.orange()
            )
        else:
            embed = discord.Embed(
                title="✅ **Wartungsmodus abgeschlossen** ✅",
                description="Der Bot ist wieder vollständig verfügbar.",
                color=discord.Color.green()
            )
        owner = await self.bot.fetch_user(530391227753955338)
        await owner.send(embed=embed)
        await self.send_dm_menu(ctx)


class MaintenanceMenu(discord.ui.View):
    def __init__(self, maintenance_cog):
        super().__init__(timeout=None)
        self.maintenance_cog = maintenance_cog

    @discord.ui.button(label="Wartung starten", style=discord.ButtonStyle.danger)
    async def start_maintenance(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.maintenance_cog.maintenance(interaction)
        await interaction.response.send_message("🔧 Wartungsmodus aktiviert!", ephemeral=True)

    @discord.ui.button(label="Wartung beenden", style=discord.ButtonStyle.success)
    async def end_maintenance(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.maintenance_cog.maintenance_end(interaction)
        await interaction.response.send_message("✅ Wartungsmodus beendet!", ephemeral=True)

    @discord.ui.button(label="Status", style=discord.ButtonStyle.primary)
    async def status(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.maintenance_cog.status(interaction)
        await interaction.response.send_message("📊 Status gesendet!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Maintenance(bot))

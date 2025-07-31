import discord
from discord.ext import commands, tasks
from discord.ui import Modal, TextInput, View, Select, Button
from datetime import datetime, timedelta
import database  # Import your database functions


class TimeReminderModal(Modal):
    def __init__(self, bot, original_message, view_message):
        super().__init__(title="Set Time-based Reminder")
        self.bot = bot
        self.original_message = original_message
        self.view_message = view_message
        self.add_item(TextInput(label="Reminder Text", placeholder="What do you want to be reminded of?"))
        self.add_item(TextInput(label="Date and Time", placeholder="YYYY-MM-DD HH:MM:SS"))

    async def on_submit(self, interaction: discord.Interaction):
        text = self.children[0].value
        time_str = self.children[1].value

        try:
            reminder_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            await interaction.response.send_message(
                "Invalid time format. Please provide a valid date and time in the format YYYY-MM-DD HH:MM:SS.",
                ephemeral=True)
            return

        database.add_reminder(str(interaction.user.id), str(interaction.channel.id),
                              reminder_time.strftime("%Y-%m-%d %H:%M:%S"), text, str(interaction.guild.id))
        interaction.client.get_cog('Reminder').load_reminders()  # Reload reminders from the database
        await interaction.response.send_message(
            f"Reminder set for {reminder_time.strftime('%Y-%m-%d %H:%M:%S')} with the text '{text}'.",
            ephemeral=True)

        try:
            await self.original_message.delete()  # Delete the original message
            await self.view_message.delete()  # Delete the view message
        except discord.errors.NotFound:
            pass  # Message already deleted


class DateReminderModal(Modal):
    def __init__(self, bot, original_message, view_message):
        super().__init__(title="Set Date-based Reminder")
        self.bot = bot
        self.original_message = original_message
        self.view_message = view_message
        self.add_item(TextInput(label="Reminder Text", placeholder="What do you want to be reminded of?"))
        self.add_item(TextInput(label="Date", placeholder="YYYY-MM-DD"))

    async def on_submit(self, interaction: discord.Interaction):
        text = self.children[0].value
        date_str = self.children[1].value

        try:
            reminder_time = datetime.strptime(date_str, "%Y-%m-%d")
            reminder_time = reminder_time.replace(hour=0, minute=0, second=0)
        except ValueError:
            await interaction.response.send_message(
                "Invalid date format. Please provide a valid date in the format YYYY-MM-DD.",
                ephemeral=True)
            return

        database.add_reminder(str(interaction.user.id), str(interaction.channel.id),
                              reminder_time.strftime("%Y-%m-%d %H:%M:%S"), text, str(interaction.guild.id))
        interaction.client.get_cog('Reminder').load_reminders()  # Reload reminders from the database
        await interaction.response.send_message(
            f"Reminder set for {reminder_time.strftime('%Y-%m-%d')} with the text '{text}'.",
            ephemeral=True)

        try:
            await self.original_message.delete()  # Delete the original message
            await self.view_message.delete()  # Delete the view message
        except discord.errors.NotFound:
            pass  # Message already deleted


class TimeOnlyReminderModal(Modal):
    def __init__(self, bot, original_message, view_message):
        super().__init__(title="Set Time-only Reminder")
        self.bot = bot
        self.original_message = original_message
        self.view_message = view_message
        self.add_item(TextInput(label="Reminder Text", placeholder="What do you want to be reminded of?"))
        self.add_item(TextInput(label="Time", placeholder="HH:MM:SS"))

    async def on_submit(self, interaction: discord.Interaction):
        text = self.children[0].value
        time_str = self.children[1].value

        try:
            reminder_time = datetime.strptime(time_str, "%H:%M:%S")
            now = datetime.now()
            reminder_time = now.replace(hour=reminder_time.hour, minute=reminder_time.minute, second=reminder_time.second)
            if reminder_time < now:
                reminder_time += timedelta(days=1)
        except ValueError:
            await interaction.response.send_message(
                "Invalid time format. Please provide a valid time in the format HH:MM:SS.",
                ephemeral=True)
            return

        database.add_reminder(str(interaction.user.id), str(interaction.channel.id),
                              reminder_time.strftime("%Y-%m-%d %H:%M:%S"), text, str(interaction.guild.id))
        interaction.client.get_cog('Reminder').load_reminders()  # Reload reminders from the database
        await interaction.response.send_message(
            f"Reminder set for {reminder_time.strftime('%H:%M:%S')} with the text '{text}'.",
            ephemeral=True)

        try:
            await self.original_message.delete()  # Delete the original message
            await self.view_message.delete()  # Delete the view message
        except discord.errors.NotFound:
            pass  # Message already deleted


class DurationReminderModal(Modal):
    def __init__(self, bot, duration_type, original_message, view_message):
        super().__init__(title="Set Duration-based Reminder")
        self.bot = bot
        self.duration_type = duration_type
        self.original_message = original_message
        self.view_message = view_message
        self.add_item(TextInput(label="Reminder Text", placeholder="What do you want to be reminded of?"))
        self.add_item(TextInput(label="Time in " + duration_type, placeholder="Enter the number of " + duration_type))

    async def on_submit(self, interaction: discord.Interaction):
        text = self.children[0].value
        duration = self.children[1].value

        try:
            duration = int(duration)
        except ValueError:
            await interaction.response.send_message("Invalid time input. Please enter a valid number.", ephemeral=True)
            return

        reminder_time = None  # Initialize reminder_time

        #print(f"Duration Type: {self.duration_type}, Duration: {duration}")  # Debugging line

        if self.duration_type.lower() == 'seconds':
            reminder_time = datetime.now() + timedelta(seconds=duration)
        elif self.duration_type.lower() == 'minutes':
            reminder_time = datetime.now() + timedelta(minutes=duration)
        elif self.duration_type.lower() == 'hours':
            reminder_time = datetime.now() + timedelta(hours=duration)
        elif self.duration_type.lower() == 'days':
            reminder_time = datetime.now() + timedelta(days=duration)
        elif self.duration_type.lower() == 'weeks':
            reminder_time = datetime.now() + timedelta(weeks=duration)

        if reminder_time is None:
            await interaction.response.send_message("Invalid duration type. Please select a valid duration.", ephemeral=True)
            return

        database.add_reminder(str(interaction.user.id), str(interaction.channel.id),
                              reminder_time.strftime("%Y-%m-%d %H:%M:%S"), text, str(interaction.guild.id))
        interaction.client.get_cog('Reminder').load_reminders()  # Reload reminders from the database
        await interaction.response.send_message(
            f"Reminder set in {duration} {self.duration_type} for '{text}'.", ephemeral=True
        )

        try:
            await self.original_message.delete()  # Delete the original message
            await self.view_message.delete()  # Delete the view message
        except discord.errors.NotFound:
            pass  # Message already deleted


class DeleteReminderSelect(Select):
    def __init__(self, bot, ctx, reminders, original_message, view_message):
        self.bot = bot
        self.ctx = ctx
        self.reminders = reminders
        self.original_message = original_message
        self.view_message = view_message

        options = [
            discord.SelectOption(label=f"{ctx.guild.get_member(int(r[0])).display_name}: {r[3]} - {r[2]}", value=f"{r[0]}|{r[2]}") for r in reminders
        ]

        super().__init__(placeholder="Select a reminder to delete...", min_values=1, max_values=1,
                         options=options)

    async def callback(self, interaction: discord.Interaction):
        value = self.values[0]
        user_id, reminder_time = value.split('|')
        database.remove_reminder(reminder_time, user_id, self.ctx.guild.id)

        interaction.client.get_cog('Reminder').load_reminders()  # Reload reminders from the database
        await interaction.response.send_message(f"Reminder for '{reminder_time}' has been deleted.", ephemeral=True)

        try:
            await self.original_message.delete()  # Delete the original message
            await self.view_message.delete()  # Delete the view message
        except discord.errors.NotFound:
            pass  # Message already deleted


class MemberSelect(Select):
    def __init__(self, members, placeholder, callback):
        self.callback_function = callback
        options = [discord.SelectOption(label=member.display_name, value=str(member.id)) for member in members]
        super().__init__(placeholder=placeholder, options=options)

    async def callback(self, interaction: discord.Interaction):
        await self.callback_function(interaction, self.values[0])


class ReminderView(View):
    def __init__(self, bot, ctx, view_message):
        super().__init__(timeout=180)  # 3 minutes timeout
        self.bot = bot
        self.ctx = ctx
        self.view_message = view_message

        time_select = Select(
            placeholder="Choose a date option...",
            options=[
                discord.SelectOption(label="Time Only", description="Reminder with only time"),
                discord.SelectOption(label="Date", description="Reminder with only date"),
                discord.SelectOption(label="Date and Time", description="Reminder with date and time"),
            ]
        )
        time_select.callback = self.time_select_callback
        self.add_item(time_select)

        self.select = Select(
            placeholder="Choose a time unit...",
            options=[
                discord.SelectOption(label="Seconds", description="Reminder in seconds"),
                discord.SelectOption(label="Minutes", description="Reminder in minutes"),
                discord.SelectOption(label="Hours", description="Reminder in hours"),
                discord.SelectOption(label="Days", description="Reminder in days"),
                discord.SelectOption(label="Weeks", description="Reminder in weeks"),
            ]
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

        check_button = Button(label="Check Reminders", style=discord.ButtonStyle.primary)
        check_button.callback = self.check_reminders
        self.add_item(check_button)

        delete_button = Button(label="Delete Reminder", style=discord.ButtonStyle.danger)
        delete_button.callback = self.delete_reminder
        self.add_item(delete_button)

        if ctx.author.guild_permissions.administrator:
            check_by_member_button = Button(label="Admin Check Reminders by Member", style=discord.ButtonStyle.primary)
            check_by_member_button.callback = self.check_reminders_by_member
            self.add_item(check_by_member_button)

            delete_by_member_button = Button(label="Admin Delete Reminders by Member", style=discord.ButtonStyle.danger)
            delete_by_member_button.callback = self.delete_reminders_by_member
            self.add_item(delete_by_member_button)

        cancel_button = Button(label="Cancel", style=discord.ButtonStyle.secondary)
        cancel_button.callback = self.cancel
        self.add_item(cancel_button)

    async def on_timeout(self):
        try:
            await self.ctx.message.delete()  # Delete the original message
            await self.view_message.delete()  # Delete the view message
        except discord.errors.NotFound:
            pass  # Message already deleted

    async def select_callback(self, interaction):
        duration_type = self.select.values[0]
        modal = DurationReminderModal(self.bot, duration_type, self.ctx.message, self.view_message)
        await interaction.response.send_modal(modal)

    async def time_select_callback(self, interaction):
        selected_option = interaction.data['values'][0]
        if selected_option == "Time Only":
            modal = TimeOnlyReminderModal(self.bot, self.ctx.message, self.view_message)
        elif selected_option == "Date":
            modal = DateReminderModal(self.bot, self.ctx.message, self.view_message)
        elif selected_option == "Date and Time":
            modal = TimeReminderModal(self.bot, self.ctx.message, self.view_message)

        await interaction.response.send_modal(modal)

    async def check_reminders(self, interaction):
        reminders = database.get_reminders()
        if interaction.user.guild_permissions.administrator:
            reminders_text = "\n".join([f"{interaction.guild.get_member(int(r[0])).display_name}: {r[3]} - {r[2]}" for r in reminders])
        else:
            reminders_text = "\n".join([f"{interaction.guild.get_member(int(r[0])).display_name}: {r[3]} - {r[2]}" for r in reminders if r[0] == str(interaction.user.id)])

        if not reminders_text:
            reminders_text = "No reminders available."

        await interaction.response.send_message(f"Available reminders:\n{reminders_text}", ephemeral=True)

    async def check_reminders_by_member(self, interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to perform this action.", ephemeral=True)
            return

        members = list({interaction.guild.get_member(int(r[0])) for r in database.get_reminders()})
        member_select = MemberSelect(members, "Select a member to check reminders...", self.show_reminders_for_member)
        view = View()
        view.add_item(member_select)
        await interaction.response.send_message("Select a user to check their reminders:", view=view, ephemeral=True)

    async def show_reminders_for_member(self, interaction, member_id):
        reminders = [r for r in database.get_reminders() if r[0] == member_id]
        reminders_text = "\n".join([f"{interaction.guild.get_member(int(r[0])).display_name}: {r[3]} - {r[2]}" for r in reminders])

        if not reminders_text:
            reminders_text = "No reminders available."

        await interaction.response.send_message(f"Available reminders for {interaction.guild.get_member(int(member_id)).display_name}:\n{reminders_text}", ephemeral=True)

    async def delete_reminder(self, interaction):
        reminders = database.get_reminders()
        if interaction.user.guild_permissions.administrator:
            user_reminders = reminders
        else:
            user_reminders = [r for r in reminders if r[0] == str(interaction.user.id)]

        if not user_reminders:
            await interaction.response.send_message("No reminders available to delete.",
                                                    ephemeral=True)
            return

        select = DeleteReminderSelect(self.bot, self.ctx, user_reminders, self.ctx.message, self.view_message)
        view = View()
        view.add_item(select)
        await interaction.response.send_message("Select a reminder to delete:", view=view, ephemeral=True)

    async def delete_reminders_by_member(self, interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to perform this action.", ephemeral=True)
            return

        members = list({interaction.guild.get_member(int(r[0])) for r in database.get_reminders()})
        member_select = MemberSelect(members, "Select a member to delete reminders...", self.delete_reminders_for_member)
        view = View()
        view.add_item(member_select)
        await interaction.response.send_message("Select a user to delete their reminders:", view=view, ephemeral=True)

    async def delete_reminders_for_member(self, interaction, member_id):
        reminders = [r for r in database.get_reminders() if r[0] == member_id]

        if not reminders:
            await interaction.response.send_message(f"No reminders available for {interaction.guild.get_member(int(member_id)).display_name}.",
                                                    ephemeral=True)
            return

        select = DeleteReminderSelect(self.bot, self.ctx, reminders, self.ctx.message, self.view_message)
        view = View()
        view.add_item(select)
        await interaction.response.send_message(f"Select a reminder to delete for {interaction.guild.get_member(int(member_id)).display_name}:", view=view, ephemeral=True)

    async def cancel(self, interaction):
        try:
            await self.ctx.message.delete()  # Delete the original message
            await self.view_message.delete()  # Delete the view message
        except discord.errors.NotFound:
            pass  # Message already deleted


class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminders = []
        self.load_reminders()
        self.check_reminders.start()

    def load_reminders(self):
        self.reminders = database.get_reminders()
        #print(f"Loaded reminders: {self.reminders}")

    @commands.command(name="remindme", help="Create a reminder or view existing reminders.")
    async def remindme(self, ctx):
        view = ReminderView(self.bot, ctx, ctx.message)
        view_message = await ctx.send(
            "Select a time unit to set a reminder or check existing reminders:",
            view=view)
        view.view_message = view_message

    @tasks.loop(seconds=1)
    async def check_reminders(self):
        current_time = datetime.now()
        for reminder in self.reminders:
            reminder_time = datetime.strptime(reminder[2], "%Y-%m-%d %H:%M:%S")
            if reminder_time <= current_time:
                user = await self.bot.fetch_user(int(reminder[0]))
                try:
                    embed = discord.Embed(
                        title="⏰ Reminder",
                        description=f"**{reminder[3]}**",
                        color=discord.Color.blue(),
                        timestamp=datetime.utcnow()
                    )
                    embed.set_footer(text=f"Sent by {self.bot.user.name}", icon_url=self.bot.user.avatar.url)
                    embed.add_field(name="Reminder Time", value=reminder[2], inline=True)
                    embed.add_field(name="Created by", value=user.mention, inline=True)
                    await user.send(embed=embed)
                except discord.errors.Forbidden:
                    channel = self.bot.get_channel(int(reminder[1]))
                    if channel:
                        await channel.send(f"{user.mention}, Reminder: {reminder[3]}")
                database.remove_reminder(reminder[2], reminder[0], reminder[4])
        self.load_reminders()  # Reload reminders from the database

    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Reminder(bot))

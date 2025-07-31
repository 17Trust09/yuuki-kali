import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import json
import asyncio
from datetime import datetime
import database

def load_todo_lists():
    try:
        with open('todo_lists.txt', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_todo_lists(todo_lists):
    with open('todo_lists.txt', 'w') as file:
        json.dump(todo_lists, file)

class todo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.todo_lists = load_todo_lists()

    async def get_prefix(bot, message):
        # Standard-Präfix, falls kein Präfix in der Datenbank gefunden wurde oder die Nachricht in DMs gesendet wurde
        default_prefix = '!'
        # Überprüfen, ob die Nachricht in einem Server (nicht in DMs) gesendet wurde
        if message.guild is None:
            return default_prefix
        server_id = str(message.guild.id)
        prefix = database.get_server_setting(server_id)  # Abrufen des Präfixes aus der Datenbank
        return prefix or default_prefix


    @commands.command(name="todo")
    async def todo_command(self, ctx):
        view = ToDoView(self.todo_lists, ctx.author.id, ctx.message)
        message = await ctx.send("Klicke auf den Button, um deine To-Do-Liste zu erstellen.", view=view)
        view.info_message = message

    @commands.command(name="edit_todo")
    async def edit_todo_command(self, ctx, message_id: int):
        todo_prefix = await self.get_prefix(ctx.message)
        message_id_str = str(message_id)
        list_to_edit = None
        for list_name, list_info in self.todo_lists.items():
            if str(list_info.get("message_id")) == message_id_str:
                list_to_edit = list_name
                break

        if list_to_edit:
            try:
                original_message = await ctx.channel.fetch_message(message_id)
                embed = original_message.embeds[0] if original_message.embeds else None
                view = ToDoTaskView(self.todo_lists, list_to_edit)
                new_message = await ctx.send(embed=embed, view=view)

                # Delete the original message and the command message
                await original_message.delete()
                await ctx.message.delete()

                # Find and store the ID of the old follow-up message
                followup_message_id = None
                async for message in ctx.channel.history():
                    if message.author == self.bot.user and "Die Liste" in message.content and f"'{list_to_edit}' wurde erstellt." in message.content:
                        followup_message_id = message.id
                        break

                if followup_message_id:
                    # Delete the old follow-up message using its ID
                    old_followup_message = await ctx.channel.fetch_message(followup_message_id)
                    await old_followup_message.delete()

                # Send a new follow-up message with the updated information
                new_followup_message = await ctx.send(
                    f"Die Liste '{list_name}' wurde erstellt. Du kannst sie mit `{todo_prefix}edit_todo {new_message.id}` bearbeiten, wenn die Buttons nicht mehr aktiv sind (Fehlermeldung: Diese Interaktion ist fehlgeschlagen).")

                # Update the message_id in the todo_lists dictionary
                self.todo_lists[list_to_edit]["message_id"] = new_message.id
                save_todo_lists(self.todo_lists)

            except discord.NotFound:
                await ctx.send("Die ursprüngliche Nachricht wurde nicht gefunden. Erstelle eine neue Nachricht.")
            except discord.Forbidden:
                pass
            except Exception as e:
                print(f"Ein Fehler ist aufgetreten: {e}")
        else:
            await ctx.send("Liste nicht gefunden.")


    async def cog_unload(self):
        pass

class ToDoView(View):
    def __init__(self, todo_lists, user_id, command_message):
        super().__init__()
        self.todo_lists = todo_lists
        self.user_id = user_id
        self.command_message = command_message
        self.info_message = None
        self.followup_message_id = None

    async def delete_messages(self):
        try:
            await self.command_message.delete()
        except discord.NotFound:
            pass
        if self.info_message:
            try:
                await self.info_message.delete()
            except discord.NotFound:
                pass

    @discord.ui.button(label="Liste erstellen", style=discord.ButtonStyle.green)
    async def create_list(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ListNameModal(self.todo_lists, self.user_id)
        await interaction.response.send_modal(modal)
        await self.delete_messages()

class ListNameModal(Modal):
    def __init__(self, todo_lists, user_id, *args, **kwargs):
        super().__init__(title="Name der To-Do-Liste", *args, **kwargs)
        self.todo_lists = todo_lists
        self.user_id = user_id
        self.followup_message_id = None  # Initialize followup_message_id to None
        self.add_item(TextInput(label="Listennamen eingeben", placeholder="Gib den Namen deiner To-Do-Liste ein"))

    async def on_submit(self, interaction: discord.Interaction):
        list_name = self.children[0].value
        if list_name not in self.todo_lists:
            embed = discord.Embed(title=list_name, description="Deine To-Do-Liste ist momentan leer.",
                                  color=discord.Color.blue())
            await interaction.response.send_message(embed=embed, view=ToDoTaskView(self.todo_lists, list_name))

            message = await interaction.original_response()  # Obtain the message from interaction

            if message:
                self.todo_lists[list_name] = {"tasks": [], "owner": self.user_id, "message_id": message.id}
                save_todo_lists(self.todo_lists)

                followup_message = await interaction.followup.send(
                    f"Die Liste '{list_name}' wurde erstellt. Du kannst sie mit `!edit_todo {message.id}` bearbeiten, wenn die Buttons nicht mehr Aktiv sind (Fehlermeldung: Diese Interaktion ist fehlgeschlagen).")

                # Assign the ID of the follow-up message to followup_message_id
                self.followup_message_id = followup_message.id
            else:
                print("Fehler: Nachricht konnte nicht gesendet werden.")
        else:
            await interaction.response.send_message(f"Eine Liste mit dem Namen '{list_name}' existiert bereits.", ephemeral=True)


class ToDoTaskView(View):
    def __init__(self, todo_lists, list_name, followup_message_id=None):
        super().__init__()
        self.todo_lists = todo_lists
        self.list_name = list_name
        self.followup_message_id = followup_message_id

    @discord.ui.button(label="Aufgabe hinzufügen", style=discord.ButtonStyle.blurple)
    async def add_task(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = TaskModal(self.todo_lists, self.list_name, "Aufgabe hinzufügen")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Aufgabe entfernen", style=discord.ButtonStyle.red)
    async def remove_task(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = TaskModal(self.todo_lists, self.list_name, "Aufgabe entfernen")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="In Bearbeitung setzen", style=discord.ButtonStyle.grey)
    async def mark_in_progress(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = TaskModal(self.todo_lists, self.list_name, "In Bearbeitung setzen")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Als abgeschlossen markieren", style=discord.ButtonStyle.green)
    async def mark_completed(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = TaskModal(self.todo_lists, self.list_name, "Als abgeschlossen markieren")
        await interaction.response.send_modal(modal)


    @discord.ui.button(label="Liste löschen", style=discord.ButtonStyle.danger)
    async def delete_list(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.list_name in self.todo_lists:
            del self.todo_lists[self.list_name]
            save_todo_lists(self.todo_lists)

            # Check if there is a follow-up message ID associated with this view
            if self.followup_message_id:
                try:
                    followup_message = await interaction.channel.fetch_message(self.followup_message_id)
                    if followup_message:
                        await followup_message.delete()
                    else:
                        print(f"Follow-up-Nachricht mit ID {self.followup_message_id} wurde nicht gefunden.")
                except discord.NotFound:
                    print(f"Nachricht mit ID {self.followup_message_id} nicht gefunden.")
                    pass

            await interaction.response.edit_message(content="To-Do-Liste wurde gelöscht.", embed=None, view=None)
            await asyncio.sleep(2)
            try:
                await interaction.message.delete()
            except discord.NotFound:
                pass


class TaskModal(Modal):
    def __init__(self, todo_lists, list_name, action, *args, **kwargs):
        super().__init__(title=action, *args, **kwargs)
        self.todo_lists = todo_lists
        self.list_name = list_name
        self.action = action

        if self.action == "Aufgabe zuweisen":
            self.add_item(TextInput(label="Aufgabe", placeholder="Gib die Aufgabennummer an"))
            self.add_item(TextInput(label="Benutzername",
                                    placeholder="Gib den Displaynamen des Benutzers ein, dem die Aufgabe zugewiesen werden soll"))
        else:
            self.add_item(TextInput(label="Aufgabe", placeholder="Gib die Details ein"))

    async def on_submit(self, interaction: discord.Interaction):
        details = self.children[0].value
        user = interaction.user  # Der Benutzer, der die Interaktion ausgelöst hat
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Aktuelle Uhrzeit

        if self.action == "Aufgabe hinzufügen":
            # Hinzufügen einer neuen Aufgabe
            self.todo_lists[self.list_name]["tasks"].append({
                "task": details,
                "assigned_to": None,
                "status": None,
                "user": None,
                "timestamp": None
            })
        else:
            try:
                task_index = int(details) - 1
                if 0 <= task_index < len(self.todo_lists[self.list_name]["tasks"]):
                    task = self.todo_lists[self.list_name]["tasks"][task_index]
                    if self.action == "In Bearbeitung setzen":
                        task["status"] = "In Bearbeitung"
                    elif self.action == "Als abgeschlossen markieren":
                        task["status"] = "Abgeschlossen"
                    task["user"] = str(user)  # Benutzernamen speichern
                    task["timestamp"] = timestamp  # Uhrzeit speichern
                else:
                    raise ValueError
            except ValueError:
                await interaction.response.send_message("Ungültige Eingabe. Bitte gib eine gültige Aufgabennummer ein.", ephemeral=True)
                return

        tasks_formatted = "\n".join([
            f"{i + 1}. 🔵 {task['task']} (In Bearbeitung - von {task['user']} am {task['timestamp']})"
            if task.get('status') == 'In Bearbeitung' and task.get('user') and task.get('timestamp') else

            f"{i + 1}. ✅ {task['task']} (Abgeschlossen - von {task['user']} am {task['timestamp']})"
            if task.get('status') == 'Abgeschlossen' and task.get('user') and task.get('timestamp') else

            f"{i + 1}. ❌ {task['task']} (Zugewiesen an: {task.get('assigned_to', 'Niemand')})"
            if task.get('assigned_to') else

            f"{i + 1}. ❌ {task['task']}"
            for i, task in enumerate(self.todo_lists[self.list_name]["tasks"])
        ])
        embed = discord.Embed(title=self.list_name, description=tasks_formatted or "Deine To-Do-Liste ist momentan leer.", color=discord.Color.blue())
        await interaction.response.edit_message(embed=embed, view=ToDoTaskView(self.todo_lists, self.list_name))


async def setup(bot):
    await bot.add_cog(todo(bot))

import discord
from discord.ext import commands, tasks
import requests
import sqlite3
from datetime import datetime, timedelta

class OllamaChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ollama_url = "http://192.168.178.69:11434/chat"
        self.timeout = timedelta(minutes=30)  # Timeout für inaktive Sitzungen
        self.db_path = "ollama_chat_sessions.db"  # SQLite-Datenbank-Datei

        # Initialisiere die Datenbank
        self.init_db()

        # Starte den Hintergrundtask, um inaktive Sitzungen zu entfernen
        self.cleanup_sessions_task.start()

    def init_db(self):
        """Initialisiert die SQLite-Datenbank für Chat-Sitzungen."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                user_id TEXT PRIMARY KEY,
                context TEXT,
                last_active TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def save_session(self, user_id, context):
        """Speichert den Chat-Kontext in der Datenbank."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (user_id, context, last_active)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            context = ?,
            last_active = ?
        """, (user_id, context, datetime.utcnow(), context, datetime.utcnow()))
        conn.commit()
        conn.close()

    def load_session(self, user_id):
        """Lädt den Chat-Kontext eines Benutzers aus der Datenbank."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT context FROM sessions WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def delete_session(self, user_id):
        """Löscht die Chat-Sitzung eines Benutzers."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

    def cleanup_inactive_sessions(self):
        """Entfernt inaktive Sitzungen aus der Datenbank."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        timeout_threshold = datetime.utcnow() - self.timeout
        cursor.execute("DELETE FROM sessions WHERE last_active < ?", (timeout_threshold,))
        conn.commit()
        conn.close()

    async def send_to_ollama(self, prompt, user_id):
        """
        Sendet eine Anfrage an die Ollama-API mit dem gesamten Verlauf.
        :param prompt: Die Eingabe des Benutzers.
        :param user_id: Die ID des Benutzers.
        :return: Die Antwort der API.
        """
        # Lade bisherigen Kontext oder starte neuen Verlauf
        context = self.load_session(user_id)
        messages = []
        if context:
            messages = eval(context)  # Sicherstellen, dass es ein Python-Objekt ist
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": "llama2",  # Ersetze mit deinem gewünschten Modell
            "messages": messages
        }

        try:
            response = requests.post(self.ollama_url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Extrahiere die Antwort
            reply = data.get("response", "Entschuldigung, ich konnte keine Antwort generieren.")
            messages.append({"role": "assistant", "content": reply})

            # Speichere den Verlauf
            self.save_session(user_id, str(messages))
            return reply
        except requests.RequestException as e:
            return f"Fehler bei der Kommunikation mit der API: {e}"

    @commands.command(name="chat", help="Sprich mit der Chat-AI!")
    async def chat(self, ctx, *, message):
        """
        Discord-Befehl, um mit Ollama zu chatten.
        :param ctx: Der Kontext des Befehls.
        :param message: Die Nachricht des Benutzers.
        """
        await ctx.typing()  # Zeigt an, dass der Bot schreibt
        user_id = str(ctx.author.id)

        # Anfrage an Ollama senden
        reply = await self.send_to_ollama(message, user_id)
        await ctx.send(reply)

    @commands.command(name="reset_chat", help="Setzt den Chat-Kontext zurück.")
    async def reset_chat(self, ctx):
        """
        Setzt den Chat-Kontext für den Benutzer zurück.
        """
        user_id = str(ctx.author.id)
        self.delete_session(user_id)
        await ctx.send("Der Chat-Kontext wurde zurückgesetzt.")

    @tasks.loop(minutes=10)
    async def cleanup_sessions_task(self):
        """Hintergrundtask, um inaktive Sitzungen zu bereinigen."""
        self.cleanup_inactive_sessions()

    @cleanup_sessions_task.before_loop
    async def before_cleanup_sessions_task(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        """Beende den Hintergrundtask, wenn die Cog entladen wird."""
        self.cleanup_sessions_task.cancel()

# Cog-Setup-Funktion
async def setup(bot):
    await bot.add_cog(OllamaChat(bot))

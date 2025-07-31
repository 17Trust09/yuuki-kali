import sqlite3
import datetime
import json
import logging


def db_connect():
    return sqlite3.connect('mein_bot.db')


def create_tables():
    conn = db_connect()
    cursor = conn.cursor()

    # Stellen Sie sicher, dass diese SQL-Anweisungen korrekt sind
    cursor.execute('''CREATE TABLE IF NOT EXISTS server_settings (
                       server_id TEXT PRIMARY KEY,
                       prefix TEXT
                       )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS anti_spam_settings (
                       server_id TEXT PRIMARY KEY,
                       message_limit INTEGER,
                       time_limit INTEGER
                       )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (
                          id INTEGER PRIMARY KEY,
                          server_id TEXT,
                          server_name TEXT,
                          feedback TEXT,
                          timestamp TEXT
                          )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS leveling (
                               user_id TEXT,
                               guild_id TEXT,
                               xp INTEGER,
                               level INTEGER,
                               PRIMARY KEY (user_id, guild_id)
                           )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS leveling_settings (
                                   guild_id TEXT PRIMARY KEY,
                                   level_channel_id TEXT
                               )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS live_checker_settings (
                           guild_id TEXT PRIMARY KEY,
                           channel_id TEXT,
                           streamers TEXT
                           )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS log_settings (
                           guild_id TEXT PRIMARY KEY,
                           log_category_id TEXT,
                           mod_role_id TEXT,
                           admin_role_id TEXT
                           )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS nuke_settings (
                           guild_id TEXT PRIMARY KEY,
                           excluded_channel_ids TEXT,
                           excluded_category_ids TEXT,
                           excluded_role_ids TEXT
                           )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS server_setup (
                           guild_id TEXT PRIMARY KEY,
                           categories TEXT,
                           roles TEXT
                           )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS streamer_settings (
                           guild_id TEXT PRIMARY KEY,
                           streamer_name TEXT
                           )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ticket_settings (
                           guild_id TEXT PRIMARY KEY,
                           ticket_message_id INTEGER,
                           mod_role_id INTEGER
                           )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS todo_lists (
                           guild_id TEXT PRIMARY KEY,
                           data TEXT
                           )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS welcome_settings (
                           guild_id TEXT PRIMARY KEY,
                           welcome_channel_id TEXT,
                           rules_channel_id TEXT,
                           member_role_id TEXT,
                           rules_message_id TEXT
                       )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS platforms (
                           guild_id TEXT PRIMARY KEY,
                           platforms TEXT
                           )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS api_keys (
                           guild_id TEXT PRIMARY KEY,
                           api_keys TEXT
                           )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS reminders (
                               user_id TEXT,
                               channel_id TEXT,
                               reminder_time TEXT,
                               text TEXT,
                               guild_id TEXT,
                               PRIMARY KEY (user_id, reminder_time, guild_id)
                               )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS giveaways (
                               guild_id TEXT,
                               message_id TEXT,
                               channel_id TEXT,
                               prize TEXT,
                               end_time TEXT,
                               PRIMARY KEY (guild_id, message_id)
                           )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS birthdays (
                               guild_id TEXT,
                               user_id TEXT,
                               birthday DATE,
                               PRIMARY KEY (guild_id, user_id)
                           )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS cog_status (
                               guild_id TEXT,
                               cog_name TEXT,
                               is_loaded BOOLEAN,
                               PRIMARY KEY (guild_id, cog_name)
                           )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS rss_feeds (
                                guild_id TEXT,
                                channel_id TEXT,
                                rss_url TEXT,
                                last_entry_id TEXT
                            )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
                                id INTEGER PRIMARY KEY,
                                user TEXT,
                                prompt TEXT,
                                response TEXT
                            )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS authorized_users (
                                user_id INTEGER PRIMARY KEY
                            )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS conversation_history (
                           user_id TEXT PRIMARY KEY,
                           conversation TEXT
                           )''')
    conn.commit()
    conn.close()


def set_spam_settings(server_id, message_limit, time_limit):
    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO anti_spam_settings (server_id, message_limit, time_limit) VALUES (?, ?, ?)",
                    (server_id, message_limit, time_limit))
        conn.commit()
    except Exception as e:
        print(f"Fehler beim Setzen der Anti-Spam-Einstellungen: {e}")
    finally:
        conn.close()

def get_spam_settings(server_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT message_limit, time_limit FROM anti_spam_settings WHERE server_id=?", (server_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else None

def update_server_setting(server_id, prefix):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO server_settings (server_id, prefix) VALUES (?, ?)",
                   (server_id, prefix))
    conn.commit()
    conn.close()

def get_server_setting(server_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT prefix FROM server_settings WHERE server_id=?", (server_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def save_feedback(server_id, server_name, feedback):
    conn = db_connect()
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO feedback (server_id, server_name, feedback, timestamp) VALUES (?, ?, ?, ?)",
                   (server_id, server_name, feedback, timestamp))
    conn.commit()
    conn.close()

def update_user_level(user_id, guild_id, xp, level):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO leveling (user_id, guild_id, xp, level) VALUES (?, ?, ?, ?)",
                   (user_id, guild_id, xp, level))
    conn.commit()
    conn.close()

def get_user_level(user_id, guild_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT xp, level FROM leveling WHERE user_id=? AND guild_id=?", (user_id, guild_id))
    row = cursor.fetchone()
    conn.close()
    return row if row else (0, 0)

def get_leaderboard(guild_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, xp, level FROM leveling WHERE guild_id = ? ORDER BY xp DESC", (guild_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def set_level_channel(guild_id, channel_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO leveling_settings (guild_id, level_channel_id) VALUES (?, ?)", (guild_id, channel_id))
    conn.commit()
    conn.close()

def get_level_channel(guild_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT level_channel_id FROM leveling_settings WHERE guild_id=?", (guild_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def set_live_checker_settings(guild_id, channel_id, streamers):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO live_checker_settings (guild_id, channel_id, streamers) VALUES (?, ?, ?)",
                   (guild_id, channel_id, ','.join(streamers)))
    conn.commit()
    conn.close()

def get_live_checker_settings(guild_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id, streamers FROM live_checker_settings WHERE guild_id=?", (guild_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else (None, '')

def set_log_settings(guild_id, log_category_id, mod_role_id, admin_role_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO log_settings (guild_id, log_category_id, mod_role_id, admin_role_id) VALUES (?, ?, ?, ?)",
                   (guild_id, log_category_id, mod_role_id, admin_role_id))
    conn.commit()
    conn.close()

def get_log_settings(guild_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT log_category_id, mod_role_id, admin_role_id FROM log_settings WHERE guild_id=?", (guild_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else (None, None, None)

def set_nuke_settings(guild_id, excluded_channel_ids, excluded_category_ids, excluded_role_ids):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO nuke_settings (guild_id, excluded_channel_ids, excluded_category_ids, excluded_role_ids) VALUES (?, ?, ?, ?)",
                   (guild_id, ','.join(map(str, excluded_channel_ids)), ','.join(map(str, excluded_category_ids)), ','.join(map(str, excluded_role_ids))))
    conn.commit()
    conn.close()

def get_nuke_settings(guild_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT excluded_channel_ids, excluded_category_ids, excluded_role_ids FROM nuke_settings WHERE guild_id=?", (guild_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return [list(map(int, row[0].split(','))) if row[0] else [],
                list(map(int, row[1].split(','))) if row[1] else [],
                list(map(int, row[2].split(','))) if row[2] else []]
    return [], [], []

def set_server_setup(guild_id, categories, roles):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO server_setup (guild_id, categories, roles) VALUES (?, ?, ?)",
                   (guild_id, categories, roles))
    conn.commit()
    conn.close()

def get_server_setup(guild_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT categories, roles FROM server_setup WHERE guild_id=?", (guild_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else (None, None)

def set_streamer_settings(guild_id, streamer_name):
    """ Speichert die Streamer-Einstellungen für einen bestimmten Server. """
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO streamer_settings (guild_id, streamer_name) VALUES (?, ?)",
                   (guild_id, streamer_name))
    conn.commit()
    conn.close()

def get_streamer_settings(guild_id):
    """ Ruft die Streamer-Einstellungen für einen bestimmten Server ab. """
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT streamer_name FROM streamer_settings WHERE guild_id=?", (guild_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else (None,)

def set_ticket_message_id(guild_id, ticket_message_id):
    conn = db_connect()  # Stellen Sie sicher, dass db_connect korrekt definiert ist
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR REPLACE INTO ticket_settings (guild_id, ticket_message_id) VALUES (?, ?)",
                       (guild_id, ticket_message_id))
        conn.commit()
    except Exception as e:
        print(f"Fehler beim Setzen der Ticket-Nachrichten-ID: {e}")
    finally:
        cursor.close()
        conn.close()

def set_ticket_settings(guild_id, ticket_message_id, mod_role_id):
    conn = db_connect()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR REPLACE INTO ticket_settings (guild_id, ticket_message_id, mod_role_id) VALUES (?, ?, ?)",
                       (guild_id, ticket_message_id, mod_role_id))
        conn.commit()
    except Exception as e:
        print(f"Fehler beim Speichern der Ticket-Einstellungen: {e}")
    finally:
        conn.close()

def get_ticket_settings(guild_id):
    conn = db_connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ticket_message_id, mod_role_id FROM ticket_settings WHERE guild_id=?", (guild_id,))
        row = cursor.fetchone()
        if row:
            ticket_message_id = int(row[0]) if row[0] else None
            mod_role_id = int(row[1]) if row[1] else None
            return (ticket_message_id, mod_role_id)
        else:
            return (None, None)
    except Exception as e:
        print(f"Fehler beim Abrufen der Ticket-Einstellungen: {e}")
        return (None, None)
    finally:
        conn.close()

def set_todo_list(guild_id, todo_list):
    """ Speichert eine To-do-Liste für einen bestimmten Server. """
    conn = db_connect()
    cursor = conn.cursor()
    data = json.dumps(todo_list)
    cursor.execute("INSERT OR REPLACE INTO todo_lists (guild_id, data) VALUES (?, ?)",
                   (guild_id, data))
    conn.commit()
    conn.close()

def get_todo_list(guild_id):
    """ Ruft die To-do-Liste für einen bestimmten Server ab. """
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM todo_lists WHERE guild_id=?", (guild_id,))
    row = cursor.fetchone()
    conn.close()
    return json.loads(row[0]) if row else None

def save_todo_list(guild_id, todo_list):
    """ Speichert eine To-do-Liste für einen bestimmten Server. """
    conn = db_connect()
    cursor = conn.cursor()
    data = json.dumps(todo_list)
    cursor.execute("INSERT OR REPLACE INTO todo_lists (guild_id, data) VALUES (?, ?)",
                   (guild_id, data))
    conn.commit()
    conn.close()

def set_welcome_settings(guild_id, welcome_channel_id, rules_channel_id, member_role_id, rules_message_id):
    """ Speichert die Einstellungen für Willkommensnachrichten. """
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO welcome_settings (guild_id, welcome_channel_id, rules_channel_id, member_role_id, rules_message_id) VALUES (?, ?, ?, ?, ?)",
                   (guild_id, welcome_channel_id, rules_channel_id, member_role_id, rules_message_id))
    conn.commit()
    conn.close()

def get_welcome_settings(guild_id):
    """ Ruft die Einstellungen für Willkommensnachrichten ab. """
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT welcome_channel_id, rules_channel_id, member_role_id, rules_message_id FROM welcome_settings WHERE guild_id=?", (guild_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else (None, None, None, None)

def set_platforms(guild_id, platforms):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO platforms (guild_id, platforms) VALUES (?, ?)",
                   (guild_id, json.dumps(platforms)))
    conn.commit()
    conn.close()

def get_platforms(guild_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT platforms FROM platforms WHERE guild_id=?", (guild_id,))
    row = cursor.fetchone()
    conn.close()
    return json.loads(row[0]) if row else []

def set_api_keys(guild_id, api_keys):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO api_keys (guild_id, api_keys) VALUES (?, ?)",
                   (guild_id, json.dumps(api_keys)))
    conn.commit()
    conn.close()

def get_api_keys(guild_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT api_keys FROM api_keys WHERE guild_id=?", (guild_id,))
    row = cursor.fetchone()
    conn.close()
    return json.loads(row[0]) if row else {}

def add_reminder(user_id, channel_id, reminder_time, text, guild_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO reminders (user_id, channel_id, reminder_time, text, guild_id) VALUES (?, ?, ?, ?, ?)",
                   (user_id, channel_id, reminder_time, text, guild_id))
    conn.commit()
    conn.close()


def get_reminders():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, channel_id, reminder_time, text, guild_id FROM reminders")
    reminders = cursor.fetchall()
    conn.close()
    return reminders


def remove_reminder(reminder_time, user_id, guild_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE reminder_time = ? AND user_id = ? AND guild_id = ?",
                   (reminder_time, user_id, guild_id))
    conn.commit()
    conn.close()

def create_giveaway(guild_id, message_id, channel_id, prize, end_time):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO giveaways (guild_id, message_id, channel_id, prize, end_time) VALUES (?, ?, ?, ?, ?)",
                   (guild_id, message_id, channel_id, prize, end_time))
    conn.commit()
    conn.close()

def get_active_giveaways():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM giveaways WHERE end_time > ?", (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
    giveaways = cursor.fetchall()
    conn.close()
    return giveaways

def remove_giveaway(guild_id, message_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM giveaways WHERE guild_id=? AND message_id=?", (guild_id, message_id))
    conn.commit()
    conn.close()

def get_giveaway(guild_id, message_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM giveaways WHERE guild_id=? AND message_id=?", (guild_id, message_id))
    row = cursor.fetchone()
    conn.close()
    return row

def add_birthday(guild_id, user_id, birthday):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO birthdays (guild_id, user_id, birthday) VALUES (?, ?, ?)", (guild_id, user_id, birthday))
    conn.commit()
    conn.close()

def get_todays_birthdays(today):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT guild_id, user_id FROM birthdays WHERE birthday = ?", (today,))
    birthdays = cursor.fetchall()
    conn.close()
    return birthdays

def remove_birthday(guild_id, user_id):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM birthdays WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
    conn.commit()
    conn.close()


def get_all_feeds():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute('SELECT guild_id, channel_id, rss_url, last_entry_id FROM rss_feeds')
    feeds = cursor.fetchall()
    conn.close()
    return feeds

def add_feed(guild_id, channel_id, rss_url, last_entry_id=""):
    conn = db_connect()
    cursor = conn.cursor()
    query = 'INSERT INTO rss_feeds (guild_id, channel_id, rss_url, last_entry_id) VALUES (?, ?, ?, ?)'
    cursor.execute(query, (guild_id, channel_id, rss_url, last_entry_id))
    conn.commit()
    conn.close()

def update_feed_last_entry_id(guild_id, channel_id, rss_url, last_entry_id):
    conn = db_connect()
    cursor = conn.cursor()
    query = 'UPDATE rss_feeds SET last_entry_id = ? WHERE guild_id = ? AND channel_id = ? AND rss_url = ?'
    cursor.execute(query, (last_entry_id, guild_id, channel_id, rss_url))
    conn.commit()
    conn.close()

def add_authorized_user(user_id):
    """Fügt einen autorisierten Benutzer zur Datenbank hinzu."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO authorized_users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def remove_authorized_user(user_id):
    """Entfernt einen autorisierten Benutzer aus der Datenbank."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM authorized_users WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def is_user_authorized(user_id):
    """Überprüft, ob ein Benutzer autorisiert ist."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM authorized_users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def save_conversation(user_id, conversation):
    """Speichert den Konversationsverlauf für einen Benutzer."""
    conn = db_connect()
    cursor = conn.cursor()
    data = json.dumps(conversation)
    cursor.execute("INSERT OR REPLACE INTO conversation_history (user_id, conversation) VALUES (?, ?)",
                   (user_id, data))
    conn.commit()
    conn.close()

def get_conversation(user_id):
    """Ruft den Konversationsverlauf für einen Benutzer ab."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT conversation FROM conversation_history WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return json.loads(row[0]) if row else []

def get_cog_status(guild_id, cog_name):
    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT is_loaded FROM cog_status WHERE guild_id=? AND cog_name=?", (guild_id, cog_name))
        row = cursor.fetchone()
        return row[0] if row else None
    except Exception as e:
        logging.error(f"Error in get_cog_status: {e}")
        return None
    finally:
        conn.close()

def update_cog_status(guild_id, cog_name, is_loaded):
    try:
        logging.debug(f"Updating cog status: {guild_id}, {cog_name}, {is_loaded}")  # Debugging-Print
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM cog_status WHERE guild_id = ? AND cog_name = ?", (guild_id, cog_name))
        exists = cursor.fetchone() is not None
        if exists:
            cursor.execute("UPDATE cog_status SET is_loaded = ? WHERE guild_id = ? AND cog_name = ?", (is_loaded, guild_id, cog_name))
        else:
            cursor.execute("INSERT INTO cog_status (guild_id, cog_name, is_loaded) VALUES (?, ?, ?)", (guild_id, cog_name, is_loaded))
        conn.commit()
    except Exception as e:
        logging.error(f"Error in update_cog_status: {e}")
    finally:
        conn.close()

def get_all_cogs_status(guild_id):
    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT cog_name, is_loaded FROM cog_status WHERE guild_id = ?", (guild_id,))
        rows = cursor.fetchall()
        logging.debug(f"Fetched all cogs status for guild_id: {guild_id} - {rows}")
        return {row[0]: bool(row[1]) for row in rows}
    except Exception as e:
        logging.error(f"Error in get_all_cogs_status: {e}")
        return {}
    finally:
        conn.close()


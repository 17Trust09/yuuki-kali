#!/usr/bin/env python3
import os
import time
import subprocess
import psutil
import logging

# Logger konfigurieren
watchdog_logger = logging.getLogger("watchdog")
watchdog_logger.setLevel(logging.INFO)
if not watchdog_logger.hasHandlers():
    fh = logging.FileHandler("watchdog.log", encoding="utf-8", mode="a")
    fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s",
                            "%Y-%m-%d %H:%M:%S")
    fh.setFormatter(fmt)
    watchdog_logger.addHandler(fh)

# Konfiguration
BOT_DIR       = "/home/kali/Desktop/Botv2"
HEARTBEAT_FILE= os.path.join(BOT_DIR, "heartbeat.txt")
LOG_FILE      = os.path.join(BOT_DIR, "discord_errors.log")
VENV_PATH     = os.path.join(BOT_DIR, "venv/bin/activate")
BOT_SCRIPT    = "main.py"
ERROR_KEYWORDS= ["rate limited"]
_last_log_check = 0

def touch_heartbeat():
    """Legt heartbeat.txt an bzw. aktualisiert den ModTime."""
    try:
        # Datei anlegen, falls sie nicht existiert
        open(HEARTBEAT_FILE, "a").close()
        # ModTime updaten
        os.utime(HEARTBEAT_FILE, None)
        watchdog_logger.info("Heartbeat-Datei aktualisiert")
    except Exception as e:
        watchdog_logger.error(f"Fehler beim Heartbeat-Touch: {e}")

def start_bot():
    watchdog_logger.info("Bot wird gestartet")
    print("Starte Bot…")
    proc = subprocess.Popen(
        ["bash", "-c",
         f"cd {BOT_DIR} && source {VENV_PATH} && python {BOT_SCRIPT}"]
    )
    # direkt nach Start Heartbeat erstellen
    touch_heartbeat()
    return proc

def is_bot_running():
    for proc in psutil.process_iter(['cmdline']):
        if proc.info['cmdline'] and BOT_SCRIPT in " ".join(proc.info['cmdline']):
            return proc
    return None

def check_heartbeat(max_age=60):
    """Gibt True zurück, wenn der Heartbeat älter als max_age ist."""
    try:
        age = time.time() - os.path.getmtime(HEARTBEAT_FILE)
        return age > max_age
    except FileNotFoundError:
        # Datei sollte immer existieren – Touch arbeitet aber dran
        return True

def check_log_for_errors(logfile_path, keywords, max_lines=50):
    global _last_log_check
    if not os.path.exists(logfile_path):
        return False
    mtime = os.path.getmtime(logfile_path)
    if mtime <= _last_log_check:
        return False
    _last_log_check = mtime

    with open(logfile_path, "r", errors="ignore") as f:
        lines = f.readlines()[-max_lines:]
    for line in lines:
        for kw in keywords:
            if kw.lower() in line.lower():
                watchdog_logger.warning(f"Fehler im Log erkannt: {line.strip()}")
                return True
    return False

def kill_proc(proc):
    if proc:
        watchdog_logger.warning("Bot wird beendet")
        print("Beende Bot…")
        proc.kill()

if __name__ == "__main__":
    watchdog_logger.info("Watchdog gestartet")
    print("Watchdog aktiv")
    bot_proc = start_bot()

    while True:
        time.sleep(10)
        running = is_bot_running()

        if running is None:
            watchdog_logger.warning("Bot nicht gefunden. Starte neu")
            print("Bot abgestürzt. Starte neu…")
            bot_proc = start_bot()
            continue

        # Prozess lebt → heartbeat neu setzen
        touch_heartbeat()

        if check_heartbeat():
            watchdog_logger.warning("Kein Heartbeat erkannt. Starte neu")
            print("Kein Heartbeat erkannt. Starte neu…")
            kill_proc(running)
            time.sleep(3)
            bot_proc = start_bot()
            continue

        if check_log_for_errors(LOG_FILE, ERROR_KEYWORDS):
            print("Fehler im Log erkannt. Starte neu…")
            kill_proc(running)
            time.sleep(3)
            bot_proc = start_bot()
            continue

#!/usr/bin/env bash
# start_watuchdog.sh

cd /home/kali/Desktop/Botv2 || exit 1
source venv/din/activate
python bot_watchdog.py
exec bash

#!/bin/bash
until python3.5 bot.py; do
    echo "'bot.py' crashed with exit code $?. Restarting..." >&2
    sleep 1
done

#!/usr/bin/env bash
until unbuffer python3.5 bot.py 2>&1 | tee botlog; do
    echo "'bot.py' crashed with exit code $?. Restarting..." >&2
    sleep 1
done

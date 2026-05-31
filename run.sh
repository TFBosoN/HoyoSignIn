#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Generate a random delay between 1 and 80 seconds
delay=$((1 + RANDOM % 80))

LOGFILE="$SCRIPT_DIR/last_job.log"

echo "Waiting for $delay seconds..." > "$LOGFILE"
sleep "$delay"

cd "$SCRIPT_DIR/src"
python3 -m __init__ >> "$LOGFILE" 2>&1

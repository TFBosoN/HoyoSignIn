#!/bin/bash

# Navigate to the directory of the script
cd "$(dirname "$0")"

# Generate a random delay between 1 and 80 seconds (you can adjust the range)
delay=$((1 + RANDOM % 80))

echo "Waiting for $delay seconds..." > last_job.log
sleep "$delay"

cd src

# Add your further commands here
python3 -m __init__ >> last_job.log 2>&1

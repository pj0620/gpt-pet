#!/bin/bash

script_dir="$(dirname "$0")"

source $script_dir/env.sh

echo "SIGINT received, stopping Flask and Docker Compose..."

# Stop Flask server
ps aux | grep 'ai2' | awk '{print $2}' | xargs kill
for port in $HARDWARE_MODULE_PORT; do
  PID=$(lsof -t -i:"$port")
  if [ -n "$PID" ]; then
      echo "Killing process on port $port with PID: $PID"
      kill $PID
  else
      echo "No process found on port $port"
  fi
done

# Run docker-compose down
docker-compose down

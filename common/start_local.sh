#!/bin/sh

# Function to run when SIGINT (Ctrl+C) is received
cleanup() {
    echo "SIGINT received, stopping Flask and Docker Compose..."

    # Stop Flask server
    ps aux | grep 'ai2' | awk '{print $2}' | xargs kill
    for port in $ENV_MODULE_PORT; do
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

    exit 0
}

# Trap SIGINT
trap cleanup INT

source ./env.sh

ps aux | grep 'ai2' | awk '{print $2}' | xargs kill

for port in $ENV_MODULE_PORT; do
    PID=$(lsof -t -i:"$port")
    if [ -n "$PID" ]; then
        echo "Killing process on port $port with PID: $PID"
        kill $PID
    else
        echo "No process found on port $port"
    fi
done

# start Environment Module
pushd ../modules/environment_module
./venv/bin/flask run -p $ENV_MODULE_PORT &
popd

pushd ..
docker-compose up
popd
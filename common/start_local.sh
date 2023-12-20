#!/bin/sh

source ./env.sh

for port in $ENV_MODULE_PORT $VISION_MODULE_PORT $VISION_PROXY_MODULE_PORT; do
    # Find process ID (PID) listening on each port and kill the process
    PID=$(lsof -t -i:"$port")
    if [ -n "$PID" ]; then
        echo "Killing process on port $port with PID: $PID"
        kill $PID
    else
        echo "No process found on port $port"
    fi
done

FLASK=../../venv/bin/flask

pushd ../modules/environment_module
$FLASK run -p $ENV_MODULE_PORT &
popd

pushd ../modules/vision_module
$FLASK run -p $VISION_MODULE_PORT &
popd

pushd ../modules/vision_proxy_module
$FLASK run -p $VISION_PROXY_MODULE_PORT &
popd

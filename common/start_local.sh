#!/bin/bash

script_dir="$(dirname "$0")"

# Function to run when SIGINT (Ctrl+C) is received
cleanup() {
  "$script_dir"/cleanup.sh
}

source "$script_dir/env.sh"

# Trap SIGINT
trap cleanup INT
cleanup

headless_mode=0
for arg in "$@"
do
  if [ "$arg" = "--headless" ]; then
    headless_mode=1
    break
  fi
done
if [ $headless_mode -eq 0 ]; then
  echo "Setting up ai2Thor + hardware module locally"
  pushd ../modules/hardware_module
  ./venv/bin/flask run -p "$HARDWARE_MODULE_PORT" &
  popd
fi

echo starting other docker-based modules
pushd ..
docker-compose up
popd
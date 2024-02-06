#!/bin/bash

# Motor-Sensory Modules
export OBJECT_PERMANENCE_MODULE_PORT=3000
export LOCATION_MODULE_PORT=3001
export VISION_MODULE_PORT=3002

# Environment Modules
export HARDWARE_MODULE_PORT=4000
export VECTOR_DB_MODULE_PORT=4001
#export SQL_MODULE_PORT=4003

# SQL Config
#export SQL_DATABASE_NAME=gptpet-db
#export SQL_USER_NAME=gptpet-user
#export SQL_PASSWORD=password


private_env_path=../../private/env.sh
if [[ -x "$private_env_path" ]]; then
    echo found private env.sh file running
    # Execute the script
    source "$private_env_path"
else
    echo "Script does not exist or is not executable."
fi

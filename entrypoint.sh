#!/bin/bash

. /app/SetupEnv.sh
cd /tmp
exec python3 /app/run.py "$@"


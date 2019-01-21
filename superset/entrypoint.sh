#!/bin/bash

#echo "[entrypoint.sh] Starting Superset..."

#gunicorn superset:app
superset-init &

echo "[entrypoint.sh] Calling CMD: $@..."

exec "$@"

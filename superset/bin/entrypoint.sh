#!/bin/bash

echo "[entrypoint.sh] Starting Superset..."

superset-init

echo "[entrypoint.sh] Calling CMD: $@..."

exec "$@"
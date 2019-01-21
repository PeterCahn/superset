#!/bin/bash

#echo "[entrypoint.sh] Starting Superset..."

#gunicorn superset:app
superset-init &

echo "[entrypoint.sh] Calling CMD: $@..."

<<<<<<< HEAD
exec "$@"
=======
exec "$@"
>>>>>>> 829da4c771cb5101f9f9025c46be43d7eb758ff6

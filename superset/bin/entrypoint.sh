#!/bin/bash

#echo "[entrypoint.sh] Starting Superset..."

if [ -z "$SUPERSET_CONFIG_PATH" ] ; then
	export SUPERSET_CONFIG_PATH=/usr/local/lib/python3.6/site-packages/superset/superset_config.py
        cp -f /usr/local/bin/custom-config.py $SUPERSET_CONFIG_PATH
else
	if [ ! -f $SUPERSET_CONFIG_PATH ] ; then
		echo "superset_config.py not found in $SUPERSET_CONFIG_PATH"
		exit
	fi
fi

# Check URI to provide an already created set of dashboards and databases to import (the URI is the DB where the data actually resides)
if [ -n "$SQLALCHEMY_DATA_URI" ] ; then
        echo "SQLALCHEMY_DATA_URI: $SQLALCHEMY_DATA_URI"
        sed -i 's|^\([[:blank:]]*\)"sqlalchemy_uri":.*$|\1"sqlalchemy_uri": "'$SQLALCHEMY_DATA_URI'",|g' /home/superset/dashboards.json
        sed -i 's|^\([[:blank:]]*\)sqlalchemy_uri:.*$|\1sqlalchemy_uri: '$SQLALCHEMY_DATA_URI'|g' /home/superset/datasources.yaml
fi


# Fix "Timestamped data with PostgreSQL backend" for version 0.28.1 (issue: https://github.com/apache/incubator-superset/issues/6284)
sed -i -e 's/utc=False/utc=True/g' /usr/local/lib/python3.6/site-packages/superset/viz.py

# Fix error when exporting yaml from datasource
sed -i 's/key=lambda k: sorted(k.items()))/key=lambda k: (k.items()))/' /usr/local/lib/python3.6/site-packages/superset/models/helpers.py

superset-init &

echo "[entrypoint.sh] Calling CMD: $@..."

exec "$@"

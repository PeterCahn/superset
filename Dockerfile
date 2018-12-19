FROM amancevice/superset

USER root

# Configure Filesystem
COPY superset/superset-init /usr/local/bin/superset-init
COPY superset/custom-config /usr/local/bin/custom-config
COPY superset/install-dremio.sh /usr/local/bin/install-dremio.sh

COPY superset/sql_lab.py /usr/local/lib/python3.6/site-packages/superset/sql_lab.py
COPY superset/dataframe.py /usr/local/lib/python3.6/site-packages/superset/dataframe.py

# Init login user + add Dremio driver and dialect
RUN chmod 755 /usr/local/bin/install-dremio.sh && \
    chmod 755 /usr/local/bin/superset-init && \
    /usr/local/bin/install-dremio.sh && \
	cat /usr/local/bin/custom-config >> /usr/local/lib/python3.6/site-packages/superset/config.py

ENV SUPERSETUSER=team1

CMD ["gunicorn", "superset:app"]
USER superset
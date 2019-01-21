FROM amancevice/superset

USER root

# Configure Filesystem
COPY superset/install-dremio.sh /usr/local/bin/install-dremio.sh
COPY superset/superset-init /usr/local/bin/superset-init
COPY superset/custom-config.py /usr/local/bin/custom-config.py
COPY superset/entrypoint.sh /usr/local/bin/entrypoint.sh

COPY superset/sql_lab.py /usr/local/lib/python3.6/site-packages/superset/sql_lab.py
COPY superset/dataframe.py /usr/local/lib/python3.6/site-packages/superset/dataframe.py

# Add Dremio driver and dialect
RUN chmod 755 /usr/local/bin/install-dremio.sh && \
    /usr/local/bin/install-dremio.sh && \
    # Add initialization and configuration files
    chmod 755 /usr/local/bin/superset-init && \
    chmod 755 /usr/local/bin/entrypoint.sh && \
    cat /usr/local/bin/custom-config.py >> /usr/local/lib/python3.6/site-packages/superset/config.py

ENV SUPERSETUSER=superset

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

#RUN find / -name "core.py"

COPY superset/superset_views_core.py /usr/local/lib/python3.6/site-packages/superset/views/core.py
COPY superset/flask_appbuilder_security_decorators.py /usr/local/lib/python3.6/site-packages/flask_appbuilder/security/decorators.py

CMD ["gunicorn", "superset:app"]
USER superset

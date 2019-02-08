FROM amancevice/superset

USER root

# Configure Filesystem
COPY superset /usr/local

# Add Dremio driver and dialect
RUN chmod 755 /usr/local/bin/install-dremio.sh && \
    /usr/local/bin/install-dremio.sh && \
    # Add initialization and configuration files
    chmod 755 /usr/local/bin/superset-init && \
    chmod 755 /usr/local/bin/entrypoint.sh && \
    cat /usr/local/bin/custom-config.py >> /usr/local/lib/python3.6/site-packages/superset/config.py

ENV SUPERSETUSER=superset

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["gunicorn", "superset:app"]

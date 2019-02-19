FROM amancevice/superset

USER root

# Configure Filesystem
COPY superset /usr/local

# Add Dremio driver, dialect and init scripts
RUN chmod 755 /usr/local/bin/install-dremio.sh /usr/local/bin/superset-init /usr/local/bin/entrypoint.sh && \
    /usr/local/bin/install-dremio.sh

ENV SUPERSETUSER=superset

# Provide the image with base datasources and dashboard for the testing environment
COPY config/datasources.yaml /home/superset
COPY config/datshboards.json /home/superset

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["gunicorn", "superset:app"]

FROM amancevice/superset:0.29.0rc7

USER root

# Configure Filesystem
COPY superset /usr/local

# Add Dremio driver, dialect and init scripts
RUN chmod 755 /usr/local/bin/install-dremio.sh /usr/local/bin/superset-init /usr/local/bin/entrypoint.sh && \
    /usr/local/bin/install-dremio.sh

ENV SUPERSETUSER=superset

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["gunicorn", "superset:app"]

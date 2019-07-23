FROM amancevice/superset:0.28.1

USER root

# Configure Filesystem
COPY superset /usr/local

# Add Dremio driver, dialect and init scripts
RUN apt-get update; apt-get install -y vim curl netcat && \
    chmod 755 /usr/local/bin/install-dremio.sh /usr/local/bin/superset-init /usr/local/bin/entrypoint.sh && \
    /usr/local/bin/install-dremio.sh

ENV SUPERSETUSER=superset
ENV TZ=Europe/Rome

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["gunicorn", "superset:app"]

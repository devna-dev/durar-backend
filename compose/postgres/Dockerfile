FROM mdillon/postgis:9.5

COPY ./postgresql.conf /etc/postgres/postgresql.conf
COPY ./backup.sh /usr/local/bin/backup
COPY ./restore.sh /usr/local/bin/restore
COPY ./psql.sh /usr/local/bin/run_psql
COPY ./list-backups.sh /usr/local/bin/list-backups

RUN chmod +x /usr/local/bin/restore && \
    chmod +x /usr/local/bin/backup && \
    chmod +x /usr/local/bin/list-backups

CMD ["postgres", "-c", "config_file=/etc/postgres/postgresql.conf"]

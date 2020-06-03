#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

# export the postgres password so that subsequent commands don't ask for it
export PGPASSWORD=$POSTGRES_PASSWORD

psql -h db -U $POSTGRES_USER $POSTGRES_DB

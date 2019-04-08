#!/usr/bin/env bash
set -u   # crash on missing env variables
set -e   # stop on any error

# set env variables for pg_* tools
export PGUSER=${DATABASE_USER:='externaldata'}
export PGDATABASE=${DATABASE_NAME:='externaldata'}
export PGHOST=${DATABASE_HOST:='database'}
export PGPASSWORD=${DATABASE_PASSWORD:='insecure'}
export TENANT_NAME=${TENENT_NAME:='BGE000081 externaldata'}
export TENANT_ID=${TENANT_ID:='12777ad76d604757a0499fb62d7ab4a9'}
export OBJECTSTORE_USER=${OBJECTSTORE_USER:='externaldata'}

python -m objectstore.archive_pgtables -t ov_ovraw ovfiets_raw parkinglocation_raw guidancesign_raw thirdparty_traveltime_raw -f backups
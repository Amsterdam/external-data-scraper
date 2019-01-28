#!/usr/bin/env bash

# Import ndw 

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

export PYTHONPATH=/app/
DIR=`dirname "$0"`

dc() {
	docker-compose -p ndw-slurp-${ENVIRONMENT} -f $DIR/docker-compose.yml $*
}

trap 'dc kill ; dc down ; dc rm -f' EXIT

dc rm -f
dc pull
dc build

# Slurp ovfiets
dc run --rm importer python data_sources/ndw/slurp.py --ndw

dc down -v
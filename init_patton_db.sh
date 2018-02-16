#!/usr/bin/env bash
sleep 10
python ./create_patton_db.py
#patton-server -C `echo $POSTGRES_URI`/patton init-db
#patton-server -C `echo $POSTGRES_URI`/patton serve&
./wait-for-it.sh postgres:5433 -- /opt/deeptracy/run.sh

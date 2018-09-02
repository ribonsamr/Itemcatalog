#!/bin/bash
if [[ $1 = -s ]]; then
  ./uninstall.sh 2> /dev/null
  exit 1
fi
pip3 uninstall flask-migrate flask-script flask-sqlalchemy flask-wtf psycopg2-binary
psql -c 'drop database main_db'
rm -r migrations

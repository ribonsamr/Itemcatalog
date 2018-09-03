#!/bin/bash
if [[ $1 = -s ]]; then
  ./uninstall.sh 2> /dev/null
  exit 1
fi
pip3 uninstall flask-migrate flask-script flask-sqlalchemy flask-wtf psycopg2-binary flask-login flask-uploads
psql -c 'drop database itemcatag_db'
rm -r migrations

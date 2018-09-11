#!/bin/bash
if [[ $1 = -s ]]; then
  ./uninstall.sh 2> /dev/null
  exit 1
fi
pip3 uninstall -y flask flask-migrate flask-script flask-sqlalchemy flask-wtf \
psycopg2-binary flask-login flask-uploads google-auth requests \
oauth2client google-api-python-client
psql -c 'drop database itemcatag_db'
rm -r migrations

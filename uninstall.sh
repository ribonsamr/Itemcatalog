#!/bin/bash
if [[ $1 = -s ]]; then
  ./uninstall.sh 2> /dev/null
  exit 1
fi
pip3 uninstall -y -r requirements.txt
psql -c 'drop database itemcatag_db'
rm -r migrations

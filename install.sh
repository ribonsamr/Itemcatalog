#!/bin/bash
if [[ $1 = -s ]]; then
  ./install.sh 2> /dev/null
  exit 1
fi

forcemigrate=false

# install python required packages
echo -e '-- Installing required packages --\n'
pip3 install flask-migrate flask-script flask-sqlalchemy flask-wtf psycopg2-binary

# create postgresql database
echo -e '\n-- Creating the database --\n'

create_database() {
  if [[ $1 = true ]]; then
    psql -c 'drop database itemcatag_db'
  fi
  psql -c 'create database itemcatag_db'
  forcemigrate=true
}

if psql -lqt | cut -d \| -f 1 | grep -qw 'itemcatag_db'; then
  printf "Database exists. Do you want to re-create it? (y/n): "
  read answer
  if [[ "${answer,,}" = 'y' ]]; then
    create_database true
  fi
else
  create_database
fi


# init the database
echo -e '\n-- Initializing the database --\n'

migrate() {
  if [[ $1 = true ]]; then
    echo "Deleting the migrations folder, and remigrating."
    rm -r migrations
  fi
  python3 manage.py db init
  python3 manage.py db migrate
  python3 manage.py db upgrade
}

migrations="migrations"
if [ -d "${migrations}" ]; then
  if [[ $forcemigrate = true ]]; then
    migrate true

  else
    printf "Migrations directory already exists, do you want to remove it? (y/n): "
    read answer
    if [[ "${answer,,}" = 'y' ]]; then
      migrate true
    else
      echo "Won't delete the migrations folder."
    fi
  fi

else
  migrate
fi

echo -e "\nInstall finished."
echo "You can now run the website using this command: python3 main.py"

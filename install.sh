#!/bin/bash
# install python required packages
echo -e '-- Installing required packages --\n'
pip3 install flask-migrate flask-script flask-sqlalchemy flask-wtf psycopg2-binary 2> /dev/null


# create postgresql database
echo -e '\n-- Creating the database --\n'

forcemigrate=false

create_database() {
  if [[ $1 = true ]]; then
    psql -c 'drop database main_db' 2> /dev/null
  fi
  psql -c 'create database main_db' 2> /dev/null
  forcemigrate=true
}

if psql -lqt 2> /dev/null | cut -d \| -f 1 | grep -qw 'main_db'; then
    read -p "Database exists. Do you want to re-create it? (y\n): " answer
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
    read -p "Migrations directory already exists, do you want to remove it? (y/n): " answer
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

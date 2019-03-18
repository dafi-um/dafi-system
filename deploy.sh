#!/usr/bin/env bash

if [ -z "$VENV" ]
then
    echo Must provide VENV=path_to_virtual_environment
    echo Aborting...
    exit 1
fi;

source $VENV/bin/activate

pip install -r requirements.txt

python manage.py migrate
python manage.py collectstatic --noinput

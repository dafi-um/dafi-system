#!/usr/bin/env bash

if ! test -f venv/bin/activate
then
  echo Please install a virtualenv first:
  echo python3 -m venv venv

  exit 1
fi

source venv/bin/activate

cd website

python manage.py runserver

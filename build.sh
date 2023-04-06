#!/bin/bash

echo "Building the project..."
pip install -r requirements.txt --use-deprecated=legacy-resolver

echo "Make Migration..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Collect Static..."
python manage.py collectstatic --noinput --clear

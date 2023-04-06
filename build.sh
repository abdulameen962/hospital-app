#!/bin/bash

echo "Building the project..."
pip install -r requirements.txt

echo "Make Migration..."
python manage.py check
python manage.py makemigrations
python manage.py migrate 

echo "Collect Static..."
python manage.py collectstatic --noinput --clear
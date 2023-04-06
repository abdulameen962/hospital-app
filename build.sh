#!/bin/bash

echo "Building the project..."
pip install -r requirements.txt --use-deprecated=legacy-resolver

echo "Make Migration..."
python3.11 manage.py makemigrations --noinput
python3.11 manage.py migrate --noinput

echo "Collect Static..."
python3.11 manage.py collectstatic --noinput --clear

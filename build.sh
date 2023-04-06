#!/bin/bash

echo "Building the project..."
pip install -r requirements.txt

echo "Collect Static..."
python manage.py collectstatic --noinput
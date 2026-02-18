#!/bin/bash

# Exit on error
set -o errexit

echo "Building the project..."
python3.12 -m pip install -r requirements.txt

echo "Collecting static files..."
python3.12 manage.py collectstatic --noinput

echo "Running migrations..."
python3.12 manage.py migrate

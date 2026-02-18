#!/bin/bash

# Exit on error
set -o errexit

echo "Creating virtual environment..."
python3.12 -m venv .venv
source .venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

# Install Playwright Chromium
export PLAYWRIGHT_BROWSERS_PATH=pw-browsers
python -m playwright install chromium


echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate

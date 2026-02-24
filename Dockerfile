# Use the official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies required for compilation and psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Collect static files for Django
RUN python manage.py collectstatic --noinput

# Command to run Gunicorn (Web Server)
# This default command can be overridden in docker-compose for the scraper service
CMD ["gunicorn", "burma_news.wsgi:application", "--bind", "0.0.0.0:8000"]

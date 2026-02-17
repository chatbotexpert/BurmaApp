@echo off
echo Starting Burma News Aggregator Services...

echo ----------------------------------------------------
echo Step 1: Performing Initial Scrape (Please wait)...
echo ----------------------------------------------------
python manage.py scrape_now

echo ----------------------------------------------------
echo Step 2: Starting Background Scheduler & Web Server...
echo ----------------------------------------------------

:: Start Scraper Scheduler in a new window
start "News Scraper Loop" python manage.py run_scheduler

:: Start Django Server in this window (or new, but keeping main open is nicer for logs)
python manage.py runserver

pause

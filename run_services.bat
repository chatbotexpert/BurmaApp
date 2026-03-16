@echo off
set PYTHONUTF8=1
chcp 65001
echo Starting Burma News Aggregator Services...

echo ----------------------------------------------------
echo Starting Background Services...
echo ----------------------------------------------------

:: Start Initial Scrape in its own window so it doesn't block the server
start "Initial Scrape" python manage.py scrape_now

:: Start Scraper Scheduler in a new window
start "News Scraper Loop" python manage.py run_scheduler

:: Start Django Server in this window
python manage.py runserver


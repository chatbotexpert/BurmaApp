from django.core.management.base import BaseCommand
from aggregator.scrapers import run_scraping
from aggregator.models import ScraperSettings
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs the scraper periodically in an infinite loop using the configured interval'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f'Starting scheduler...'))
        
        try:
            while True:
                # Get or create settings
                settings_obj = ScraperSettings.objects.first()
                if not settings_obj:
                    settings_obj = ScraperSettings.objects.create(scraping_interval=60)
                    self.stdout.write(self.style.WARNING(f'No settings found, created default with 60 mins interval'))
                
                interval_minutes = settings_obj.scraping_interval
                interval_seconds = interval_minutes * 60
                
                self.stdout.write(f'--- Starting scrape run at {time.strftime("%Y-%m-%d %H:%M:%S")} (Interval: {interval_minutes}m) ---')
                try:
                    count = run_scraping()
                    self.stdout.write(self.style.SUCCESS(f'Successfully scraped {count} new posts'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error during scraping: {e}'))
                    logger.error(f'Scheduler scraping error: {e}')
                
                # Re-fetch interval before sleeping in case it changed during the run
                # (Though usually we sleep after runner, so next loop will pick it up)
                
                self.stdout.write(f'Sleeping for {interval_minutes} minutes...')
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Scheduler stopped by user'))

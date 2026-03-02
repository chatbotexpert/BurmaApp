from django.core.management.base import BaseCommand
from aggregator.scrapers import run_scraping
from aggregator.models import ScraperSettings, Post
from django.utils import timezone
from datetime import timedelta
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
                    settings_obj = ScraperSettings.objects.create(scraping_interval=5) # Default to 5 minutes
                    self.stdout.write(self.style.WARNING(f'No settings found, created default with 5 mins interval'))
                
                interval_minutes = settings_obj.scraping_interval
                interval_seconds = interval_minutes * 60
                
                # --- NEW: Delete old posts logic ---
                retention_days = settings_obj.delete_old_posts_after_days
                if retention_days > 0:
                    cutoff_date = timezone.now() - timedelta(days=retention_days)
                    deleted_count, _ = Post.objects.filter(created_at__lt=cutoff_date).delete()
                    if deleted_count > 0:
                        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_count} old posts (older than {retention_days} days).'))
                
                self.stdout.write(f'--- Starting scrape run at {time.strftime("%Y-%m-%d %H:%M:%S")} (Interval: {interval_minutes}m) ---')
                try:
                    count = run_scraping()
                    self.stdout.write(self.style.SUCCESS(f'Successfully scraped {count} new posts'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error during scraping: {e}'))
                    logger.error(f'Scheduler scraping error: {e}')
                
                # Re-fetch interval before sleeping in case it changed during the run
                settings_obj.refresh_from_db()
                interval_minutes = settings_obj.scraping_interval
                interval_seconds = interval_minutes * 60
                
                self.stdout.write(f'Sleeping for {interval_minutes} minutes...')
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Scheduler stopped by user'))

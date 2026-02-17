from django.core.management.base import BaseCommand
from aggregator.scrapers import run_scraping
import time

class Command(BaseCommand):
    help = 'Runs the scraper once immediately.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting single scrape run...'))
        try:
            start_time = time.time()
            count = run_scraping()
            elapsed = time.time() - start_time
            self.stdout.write(self.style.SUCCESS(f'Done! Successfully scraped {count} new posts in {elapsed:.2f}s'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during scraping: {e}'))

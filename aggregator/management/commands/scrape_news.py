from django.core.management.base import BaseCommand
from aggregator.scrapers import run_scraping

class Command(BaseCommand):
    help = 'Scrape news from active sources'

    def handle(self, *args, **options):
        self.stdout.write('Starting scraping...')
        count = run_scraping()
        self.stdout.write(self.style.SUCCESS(f'Successfully scraped {count} new posts'))

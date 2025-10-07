# management/commands/scrape_pinkbike.py
from django.core.management.base import BaseCommand
from bikeaggr.models import PBBike
from bikeaggr.scraper import scrape_listings  # your scrape function

class Command(BaseCommand):
    help = "Scrape Pinkbike Buy/Sell listings"

    def handle(self, *args, **kwargs):
        url = "https://www.pinkbike.com/buysell/list/?category=2"
        listings = scrape_listings(url)

        for item in listings:
            PBBike.objects.update_or_create(
                url=item["url"],
                defaults={
                    "title": item["title"],
                    "price": item["price"],
                    "location": item["location"]
                }
            )
        self.stdout.write(self.style.SUCCESS("Scraping complete!"))
from django.core.management.base import BaseCommand
from app.services.purge import purge_cache

class Command(BaseCommand):
    help = "Purge cache if needed"

    def handle(self, *args, **options):
        purge_cache()

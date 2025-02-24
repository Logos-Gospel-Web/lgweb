import urllib.request
from os import environ

from django.core.management.base import BaseCommand

_main_url = environ.get('MAIN_URL', 'main:8000')

class Command(BaseCommand):
    help = "Purge cache if needed"

    def handle(self, *args, **options):
        urllib.request.urlopen(f'http://{_main_url}/private/purge').close()

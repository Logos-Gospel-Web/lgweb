
import subprocess
import urllib
import urllib.parse
import urllib.request
import json

from django.core.management.base import BaseCommand
from app.models import Analytics

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def get_country(ips):
    output = dict()
    try:
        prefix = 'https://get.geojs.io/v1/ip/country.json?ip='
        query_str = ','.join((urllib.parse.quote(ip) for ip in ips))
        sock = urllib.request.urlopen(prefix + query_str)
        result: bytes = sock.read()
        sock.close()
        data = json.loads(result)
        for item in data:
            output[item['ip']] = item.get('country', 'XX')
    finally:
        return output

class Command(BaseCommand):
    help = "Generate isbot and country"

    def handle(self, *args, **options):
        # generate isbot
        p = subprocess.Popen(['node', 'index.mjs'], cwd='lib/isbot', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        qs = Analytics.objects.filter(isbot__isnull=True).all()
        has_item = False
        for item in qs:
            has_item = True
            p.stdin.write(item.user_agent.encode() + b'\n')
            p.stdin.flush()
            output = p.stdout.readline().decode().rstrip()
            isbot = output == '1'
            item.isbot = isbot
        p.terminate()
        if has_item:
            Analytics.objects.bulk_update(qs, ['isbot'])

        # generate country
        qs = Analytics.objects.filter(isbot=False, country='').all()
        countries = dict()
        for item in qs:
            countries[item.ip] = ''
        if len(countries) > 0:
            ips = list(countries.keys())
            n = 100
            for chunk in (ips[i:i + n] for i in range(0, len(ips), n)):
                result = get_country(chunk)
                countries.update(result)
            for item in qs:
                item.country = countries[item.ip]
            Analytics.objects.bulk_update(qs, ['country'])


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

def generate_isbot():
    qs = Analytics.objects.filter(isbot__isnull=True).all()
    agents = dict()
    for item in qs:
        if item.user_agent not in agents:
            agents[item.user_agent] = []
        agents[item.user_agent].append(item)

    if len(agents) > 0:
        p = subprocess.Popen(['node', 'index.mjs'], cwd='lib/isbot', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        for chunk in chunks(list(agents.keys()), 100):
            for agent in chunk:
                p.stdin.write(agent.encode() + b'\n')
            p.stdin.flush()
            for agent in chunk:
                output = p.stdout.read(1)
                isbot = output == b'1'
                items = agents[agent]
                for item in items:
                    item.isbot = isbot
                Analytics.objects.bulk_update(items, ['isbot'])
        p.terminate()

def generate_country():
    qs = Analytics.objects.filter(isbot=False, country='').all()
    ips = dict()
    for item in qs:
        if item.ip not in ips:
            ips[item.ip] = []
        ips[item.ip].append(item)

    if len(ips) > 0:
        for chunk in chunks(list(ips.keys()), 100):
            result = get_country(chunk)
            for ip in chunk:
                items = ips[ip]
                for item in items:
                    item.country = result[item.ip]
                Analytics.objects.bulk_update(items, ['country'])


class Command(BaseCommand):
    help = "Generate isbot and country"

    def handle(self, *args, **options):
        generate_isbot()
        generate_country()

import subprocess
import urllib.parse
import urllib.request
import json

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Value

from app.models import Analytics, AnalyticsTemp

def _chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def _get_country(ips):
    output = dict()
    try:
        prefix = 'https://get.geojs.io/v1/ip/country.json?ip='
        query_str = ','.join((urllib.parse.quote(ip) for ip in ips))
        with urllib.request.urlopen(prefix + query_str) as sock:
            result: bytes = sock.read()
        data = json.loads(result)
        for item in data:
            output[item['ip']] = item.get('country', 'XX')
    finally:
        return output

def _generate_isbot():
    qs = Analytics.objects.filter(isbot__isnull=True).all()
    agents = dict()
    for item in qs:
        if item.user_agent not in agents:
            agents[item.user_agent] = []
        agents[item.user_agent].append(item)

    if len(agents) > 0:
        p = subprocess.Popen(['node', 'index.mjs'], cwd='lib/isbot', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        for chunk in _chunks(list(agents.keys()), 100):
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

def _generate_country():
    qs = Analytics.objects.filter(isbot=Value(0), country=Value('')).all()
    ips = dict()
    for item in qs:
        if item.ip not in ips:
            ips[item.ip] = []
        ips[item.ip].append(item)

    if len(ips) > 0:
        for chunk in _chunks(list(ips.keys()), 100):
            result = _get_country(chunk)
            for ip in chunk:
                items = ips[ip]
                for item in items:
                    item.country = result[item.ip]
                Analytics.objects.bulk_update(items, ['country'])

_analytics_fields = ['id', 'created_at', 'ip', 'fingerprint', 'language', 'url', 'user_agent', 'referrer']

@transaction.atomic
def _move_analytics():
    qs = AnalyticsTemp.objects.all()
    items = [Analytics(**{ k: getattr(item, k) for k in _analytics_fields }) for item in qs]
    Analytics.objects.bulk_create(items)
    qs.delete()

class Command(BaseCommand):
    help = "Move analytics and generate isbot and country"

    def handle(self, *args, **options):
        _move_analytics()
        _generate_isbot()
        _generate_country()

from pathlib import Path
import random
import string
from django.conf import settings
from django.db.models import signals
from django.dispatch import receiver
from .models import Banner
from .services.subfont import make_subfont

_subfont_base_path = Path('banner') / 'subfont'

@receiver(signals.pre_save, sender=Banner)
def banner_pre_save(sender, instance, **kwargs):
    if instance.font and not instance.subfont:
        name = ''.join(random.choices(string.ascii_letters, k=20)) + Path(instance.font.name).suffix
        instance.subfont.name = str(_subfont_base_path / name)
    elif instance.subfont and not instance.font:
        instance.subfont.name = None

@receiver(signals.post_save, sender=Banner)
def banner_post_save(sender, instance, **kwargs):
    if instance.subfont:
        (Path(settings.MEDIA_ROOT) / _subfont_base_path).mkdir(parents=True, exist_ok=True)
        make_subfont(instance.font.path, instance.subfont.path, instance.title)

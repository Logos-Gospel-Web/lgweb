from pathlib import Path
from django.conf import settings
from django.core.cache import caches
from django.db.models import signals
from django.dispatch import receiver
from .models import Banner, Contact, Analytics
from .services.subfont import make_subfont

from .services.random_string import random_string

_subfont_base_path = Path('banner') / 'subfont'

@receiver(signals.pre_save, sender=Banner)
def banner_pre_save(sender, instance, **kwargs):
    if instance.font and not instance.subfont:
        name = random_string() + Path(instance.font.name).suffix
        instance.subfont.name = str(_subfont_base_path / name)
    elif instance.subfont and not instance.font:
        instance.subfont.name = None

@receiver(signals.post_save, sender=Banner)
def banner_post_save(sender, instance, **kwargs):
    if instance.subfont:
        (Path(settings.MEDIA_ROOT) / _subfont_base_path).mkdir(parents=True, exist_ok=True)
        make_subfont(instance.font.path, instance.subfont.path, instance.title)

_module_name = __name__[:__name__.rindex('.') + 1]

@receiver(signals.post_save)
def message_post_save(sender, instance, **kwargs):
    if sender not in (Contact, Analytics) and getattr(sender, '__module__', None).startswith(_module_name):
        caches['default'].clear()
        caches['etag'].clear()

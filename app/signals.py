import os
from pathlib import Path
from django.core.cache import caches
from django.core.files.uploadedfile import TemporaryUploadedFile, UploadedFile
from django.db.models import signals
from django.dispatch import receiver
from .models import Banner, Contact, Analytics, AnalyticsTemp
from .services.subfont import make_subfont

from .services.random_string import random_string

@receiver(signals.pre_save, sender=Banner)
def banner_pre_save(sender, instance, **kwargs):
    if instance.font:
        if not isinstance(instance.font.file, UploadedFile):
            return

        if instance.subfont:
            instance.subfont.delete(save=False)

        font_file: UploadedFile = instance.font.file # TemporaryUploadedFile
        subfont_name = random_string() + Path(instance.font.name).suffix
        subfont_file = TemporaryUploadedFile(subfont_name, font_file.content_type, 0, font_file.charset, font_file.content_type_extra)
        make_subfont(font_file.file.name, subfont_file.file.name, instance.title)
        subfont_file.size = os.path.getsize(subfont_file.file.name)
        instance.subfont.name = subfont_name
        instance.subfont.file = subfont_file
        instance.subfont._committed = False
    elif instance.subfont:
        instance.subfont.delete(save=False)

_module_name = __name__[:__name__.rindex('.') + 1]

@receiver(signals.post_save)
def app_post_save(sender, instance, **kwargs):
    if sender not in (Contact, Analytics, AnalyticsTemp) and getattr(sender, '__module__', None).startswith(_module_name):
        caches['default'].clear()
        caches['etag'].clear()

# Generated by Django 5.1.4 on 2025-01-02 02:11

from django.db import migrations, models
from django.apps.registry import Apps
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from app.services.convert_search_text import convert_search_text


def add_search(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    Message = apps.get_model('app', 'Message')
    for message in Message.objects.all():
        message.search_tc = convert_search_text(message.title_tc, message.content_tc)
        message.search_sc = convert_search_text(message.title_sc, message.content_sc)
        message.save(update_fields=['search_tc', 'search_sc'])

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_banner_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='search_tc',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='message',
            name='search_sc',
            field=models.TextField(blank=True),
        ),
        migrations.RunPython(add_search),
    ]

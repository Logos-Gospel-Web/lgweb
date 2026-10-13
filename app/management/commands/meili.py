from django.core.management.base import BaseCommand
from app.models import Message
from app.services.meilisearch import meili_delete_messages, meili_update_messages

class Command(BaseCommand):
    help = "Update all messages on meilisearch"

    def handle(self, *args, **options):
        meili_update_messages(Message.objects.all())

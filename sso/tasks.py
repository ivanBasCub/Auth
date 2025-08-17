from celery import shared_task
from .views import refresh_token
from .models import EveCharater
from django.utils import timezone
from datetime import timedelta

@shared_task
def tokens():
    now = timezone.now()

    list_characters = EveCharater.objects.all()

    for character in list_characters:
        refresh_token(character)

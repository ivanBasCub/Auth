from celery import shared_task
from .views import refresh_token
from .models import EveCharater

@shared_task
def tokens():
    list_characters = EveCharater.objects.all()

    for character in list_characters:
        refresh_token(character)

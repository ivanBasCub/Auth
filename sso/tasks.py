from celery import shared_task
from .views import refresh_token, inactive_user
from .models import EveCharater

@shared_task
def tokens():
    list_characters = EveCharater.objects.all()

    for character in list_characters:
        refresh_token(character)

@shared_task
def inactive():
    inactive_user()
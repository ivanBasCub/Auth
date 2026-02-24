from celery import shared_task
from .views import refresh_token
from .models import Eve_Character

@shared_task
def tokens():
    list_characters = Eve_Character.objects.all()

    for character in list_characters:
        refresh_token(character)

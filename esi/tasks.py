from celery import shared_task
from .views import fit_list, update_character_skills
from sso.models import EveCharater

@shared_task
def fits():
    fit_list()

@shared_task
def character_skill_list():
    list_character = EveCharater.objects.all()

    for character in list_character:
        character = update_character_skills(character)
        character.save()
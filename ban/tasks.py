from celery import shared_task
import esi.views as esi_views
from sso.models import EveCharater

@shared_task
def check_transfers():
    list_pj = EveCharater.objects.all()

    for pj in list_pj:
        esi_views.transfers(pj)
    
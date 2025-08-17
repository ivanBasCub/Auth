from celery import shared_task
from .views import fit_list

@shared_task
def fits():
    fit_list()
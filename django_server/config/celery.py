import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update_fits': {
        'task' : 'esi.tasks.fits',
        'schedule': 3600,
        'args' : ()
    },
    'update_tokens': {
        'task' : 'sso.tasks.tokens',
        'schedule': 600,
        'args' : ()
    },
    'update_character_skills':{
        'task' : 'esi.tasks.character_skill_list',
        'schedule' : 86400,
        'args' : ()
    },
    'check_transfers':{
        'task' : 'ban.tasks.check_transfers',
        'schedule': 3600,
        'args': ()
    },
    'update_skillplans': {
        'task': 'esi.tasks.refresh_skillplans',
        'schedule': 7200,
        'args': ()
    },
    'update_member_assets': {
        'task': 'corp.tasks.update_member_assets',
        'schedule': 43200,
        'args': ()
    }
}

app.conf.timezone = 'Europe/Madrid'

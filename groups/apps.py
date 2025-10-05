from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_initial_groups(sender, **kwargs):
    from django.contrib.auth.models import Group
    grupos = ["Miembro", "Director", "MainFC", "FC", "Reclutador","Reserva Imperial"]

    for grupo in grupos:
        Group.objects.get_or_create(name=grupo)

class SsoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sso'

    def ready(self):
        post_migrate.connect(create_initial_groups, sender=self)

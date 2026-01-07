from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_initial_fleet_types(sender, **kwargs):
    from .models import FleetType
    fleet_types = ["Roam", "CTA", "Strat-Op", "Home Defense"]

    for fleet_type in fleet_types:
        FleetType.objects.get_or_create(name=fleet_type)


class FatsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fats'

    def ready(self):
        post_migrate.connect(create_initial_fleet_types, sender=self)

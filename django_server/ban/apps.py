from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_initial_ban_categories(sender, **kwargs):
    from .models import Category
    categories = ["RMT", "Multa", "Comportamiento inapropiado", "Spam", "60 días NO Fleet", "Black list No actividad"]

    for category in categories:
        Category.objects.get_or_create(name=category)

class BanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ban'

    def ready(self):
        post_migrate.connect(create_initial_ban_categories, sender=self)

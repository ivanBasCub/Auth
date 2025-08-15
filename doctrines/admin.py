from django.contrib import admin
import doctrines.models as doctrine_models
# Register your models here.

admin.site.register(doctrine_models.Categories)
admin.site.register(doctrine_models.FitShip)
admin.site.register(doctrine_models.Doctrine)
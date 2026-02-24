from django.contrib import admin
import doctrines.models as doctrine_models
# Register your models here.

admin.site.register(doctrine_models.Category)
admin.site.register(doctrine_models.Fit)
admin.site.register(doctrine_models.Doctrine)
from django.contrib import admin
import fats.models as models
# Register your models here.
admin.site.register(models.FleetType)
admin.site.register(models.Fleet)
admin.site.register(models.SRP)
admin.site.register(models.SRP_Ship)
admin.site.register(models.Fat_Character)
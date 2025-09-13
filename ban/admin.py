from django.contrib import admin
from .models import BannedCharacter, BanCategory, Suspicious, SuspiciousNotification

# Register your models here.
admin.site.register(BannedCharacter)
admin.site.register(BanCategory)
admin.site.register(Suspicious)
admin.site.register(SuspiciousNotification)
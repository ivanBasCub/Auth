from django.contrib import admin
from .models import BannedCharacter, BanCategory

# Register your models here.
admin.site.register(BannedCharacter)
admin.site.register(BanCategory)
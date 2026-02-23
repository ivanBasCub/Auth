from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.fat_list, name="fats_report"),
    path('add/', views.add_fat, name="add_fat"),
]
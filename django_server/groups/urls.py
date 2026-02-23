from django.urls import path
from . import views

urlpatterns = [
    path('', views.group_list, name="group-list"),
    path('requests/', views.group_nofitication_list, name="list-group-notifications")
]
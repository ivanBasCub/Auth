from django.urls import path
from . import  views

urlpatterns = [
    path('requests/', views.applications_list, name="view requests applications"),
    path('ice/request/',views.applications_request, name="old members requests"),
    path('fridge/',views.frigde, name="fridge")
]
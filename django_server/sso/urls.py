from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.eve_login, name='eve_login'),
    path('callback/', views.eve_callback, name='eve_callback'),
    path('logout/', views.eve_logout, name="eve_logout"),
]
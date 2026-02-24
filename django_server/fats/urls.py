from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.fat_list, name="fats_report"),
    path('add/', views.add_fat, name="add_fat"),
    # SRP URLs
    path('srp/', views.srp_index, name="srp_report"),
    path('srp/<str:srp_id>/view/', views.srp_view, name="srp_view"),
    path('srp/<str:srp_id>/request/', views.srp_request, name="srp_request"),
    path('srp/<str:srp_id>/admin/', views.srp_admin, name="srp_admin"),
]
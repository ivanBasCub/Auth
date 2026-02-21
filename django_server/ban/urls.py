from django.urls import path
from . import views

urlpatterns = [
    path("list/", views.banlist, name="List of bans"),
    path("add/",views.add_ban, name="Add new ban member"),
    path('del/<int:ban_id>/', views.del_ban, name="Del ban"),
    path('list/category/', views.ban_categories, name="View lists of ban categories"),
    path('list/category/add/', views.add_ban_category, name="Add new type of ban"),
    path('list/category/del/<int:category_id>/', views.del_ban_category, name="Del type of ban")
]
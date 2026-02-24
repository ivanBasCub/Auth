from django.urls import path
from . import views

urlpatterns = [
    path('', views.skill_plan_list, name="list-skillplans"),
    path('add/', views.add_skill_plan, name="add-skillplans"),
    path('edit/<int:skillplanid>/', views.edit_skill_plan, name="mod-skillplans"),
    path('del/<int:skillplanid>/', views.del_skill_plan, name="del-skillplans"),
]
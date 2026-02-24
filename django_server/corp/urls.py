from django.urls import path
from . import views

urlpatterns = [
    # Reports
    path('reports/show/members/', views.report_members_list, name="member_report"),
    path('reports/show/fats/', views.fats_reports, name="fats_report"),
    path('reports/show/skillplans/', views.skillplan_reports, name="fats_report"),
    path('reports/show/groups/', views.groups_report, name="groups_report"),
    
    # User control
    path('admin/users/', views.user_control_list, name="control-users"),

]
"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import sso.views as sso_views
import web.views as web_views
from django.conf import settings

urlpatterns = [
    path('', web_views.index, name="main"),
    path('sso/login/', sso_views.eve_login, name='eve_login'),
    path('sso/callback/', sso_views.eve_callback, name='eve_callback'),
    path('sso/logout/', sso_views.eve_logout, name="eve_logout"),
    path('auth/dashboard/', web_views.dashboard, name="dashboard"),
    path("auth/characters/main/", web_views.change_main, name="change-main"),
    # Character Audit
    path('auth/audit/', web_views.audit_account, name="audit"),
    path('auth/audit/skillplans/', web_views.skill_plan_checkers, name="skill_checker"),
    # Doctrinas y fiteos
    path('auth/doctrine/', include('doctrines.urls')),
    # CORP
    # Ban Feature
    path("auth/corp/ban/", include("ban.urls")),
    
    
    ## Zona de administración de corp
    path('auth/corp/admin/users/', web_views.user_control_list, name="control-users"),
    ## Reports
    path('auth/corp/reports/show/1/', web_views.report_members_list, name="member_report"),
    path('auth/corp/reports/show/2/', web_views.fats_reports, name="fats_report"),
    path('auth/corp/reports/show/3/', web_views.skillplan_reports, name="fats_report"),
    path('auth/corp/reports/show/4/', web_views.groups_report, name="groups_report"),
    path('auth/corp/reports/show/5/', web_views.report_member_data, name="member_data_report"),
    # Zona de Fats
    path('auth/fats/list/', web_views.fat_list, name="fat_list"),
    path('auth/fats/add/', web_views.add_fat, name="add_fat"),
    # Groups
    path('auth/groups/', web_views.group_list, name="group-list"),
    path('auth/group/management/requests/', web_views.group_nofitication_list, name="list-group-notifications"),
    # Skillplan
    path('auth/admin/skillplans/', web_views.skill_plan_list, name="list-skillplans"),
    path('auth/admin/skillplans/add/', web_views.add_skill_plan, name="add-skillplans"),
    path('auth/admin/skillplans/mod/<int:skillplanid>/', web_views.mod_skill_plan, name="mod-skillplans"),
    path('auth/admin/skillplans/del/<int:skillplanid>/', web_views.del_skill_plan, name="del-skillplans"),
    # Suspicious Transfers
    path('auth/corp/suspiciuos/notifications/',web_views.suspicious_notification_list, name="suspicious list"),
    # SRP
    path('auth/srp/', web_views.srp_index, name="srp-index"),
    path('auth/srp/<str:srp_id>/view/', web_views.srp_view, name="srp-index"),
    path('auth/srp/<str:srp_id>/request/', web_views.srp_request, name="srp-index"),
    path('auth/srp/<str:srp_id>/admin/', web_views.srp_admin, name="srp-index"),
    # Recruitment
    path('auth/recruitment/requests/', web_views.applications_list, name="recruitment"),
    path('auth/recruitment/ice/request/', web_views.applications_request, name="ice-applications"),
    path('auth/recruitment/fridge/', web_views.frigde, name="fridgge"),
]

if settings.DEBUG:
    urlpatterns += [
            path('admin/', admin.site.urls),
    ]
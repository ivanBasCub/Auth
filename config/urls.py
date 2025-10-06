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
from django.urls import path
import sso.views as sso_views
import web.views as web_views

urlpatterns = [
    path('', web_views.index, name="main"),
    path('admin/', admin.site.urls),
    path('sso/login/', sso_views.eve_login, name='eve_login'),
    path('sso/callback/', sso_views.eve_callback, name='eve_callback'),
    path('sso/logout/', sso_views.eve_logout, name="eve_logout"),
    path('auth/dashboard/', web_views.dashboard, name="dashboard"),
    path("auth/characters/main/", web_views.change_main, name="change-main"),
    # Character Audit
    path('auth/audit/', web_views.audit_account, name="audit"),
    path('auth/audit/skillplans/', web_views.skill_plan_checkers, name="skill_checker"),
    # Doctrinas y fiteos
    path('auth/fittings/', web_views.fittings, name="list_fits"),
    path('auth/fittings/doctrine/<int:doc_id>/', web_views.doctrine, name="info_doctrine"),
    path('auth/fittings/fit/<int:fit_id>/', web_views.fit, name="fit_info"),
    path('auth/fittings/admin/', web_views.admin_doctrines, name="admin fittings"),
    path('auth/fittings/admin/doctrine/add/', web_views.add_doctrine, name="new_doctrine"),
    path('auth/fittings/admin/doctrine/mod/<int:doctrine_id>/', web_views.mod_doctrine, name="mod_doctrine"),
    path('auth/fittings/admin/doctrine/del/<int:doctrine_id>/', web_views.del_doctrine, name="del_doctrine"),
    path('auth/fittings/admin/category/add/', web_views.add_category, name="new_category"),
    path('auth/fittings/admin/category/mod/<int:category_id>/', web_views.mod_category, name="mod_category"),
    path('auth/fittings/admin/category/del/<int:category_id>/', web_views.del_category, name="del_category"),
    path('auth/fittings/fit/mod/<int:fit_id>/', web_views.mod_fit, name="mod_fit"),
    # Zona de administración de corp
    path('auth/corp/banlist/', web_views.banlist, name="banlist"),
    path('auth/corp/ban/add/', web_views.add_ban, name="add_ban"),
    path('auth/corp/ban/del/<int:ban_id>/', web_views.del_ban, name="del_ban"),
    path('auth/corp/banlist/categories/', web_views.ban_categories, name="ban_categories"),
    path('auth/corp/ban/category/add/', web_views.add_ban_category, name="add_ban_category"),
    path('auth/corp/ban/category/del/<int:category_id>/', web_views.del_ban_category, name="del_ban_category"),
    # Zona de Fats
    path('auth/fats/list/', web_views.fat_list, name="fat_list"),
    path('auth/fats/add/', web_views.add_fat, name="add_fat"),
    # Corp members
    path('auth/corp/memberlist/', web_views.member_list, name="memberlist"),
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
    path('auth/corp/suspiciuos/list/', web_views.suspicious_list, name="list-suspiciuos"),
    path('auth/corp/suspiciuos/list/add/', web_views.add_suspicious, name="add-suspiciuos"),
    path('auth/corp/suspiciuos/list/del/<int:susp_id>/', web_views.del_suspicious, name="delete-suspiciuos"),
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
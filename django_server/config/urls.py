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
import web.views as web_views
from django.conf import settings

urlpatterns = [
    path('', web_views.index, name="main"),
    path('auth/dashboard/', web_views.dashboard, name="dashboard"),
    path("auth/characters/main/", web_views.change_main, name="change-main"),
    # Character Audit
    path('auth/audit/', web_views.audit_account, name="audit"),
    path('auth/audit/skillplans/', web_views.skill_plan_checkers, name="skill_checker"),
    # Login URLs
    path('sso/', include('sso.urls')),
    # Doctrine and fits
    path('auth/doctrine/', include('doctrines.urls')),
    # Fleet
    path('auth/fats/', include('fats.urls')),
    # Ban
    path("auth/corp/ban/", include("ban.urls")),
    # Groups
    path('auth/corp/groups/', include('groups.urls')),
    # Report
    path('auth/corp/', include('corp.urls')),
    # Skillplan
    path('auth/corp/skillplans/', include('skillplans.urls')),
    # Recruitment
    path('auth/recruitment/', include('recruitment.urls')),
]

if settings.DEBUG:
    urlpatterns += [
            path('admin/', admin.site.urls),
    ]
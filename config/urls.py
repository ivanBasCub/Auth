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
    path('admin/', admin.site.urls),
    path('sso/login/', sso_views.eve_login, name='eve_login'),
    path('sso/callback/', sso_views.eve_callback, name='eve_callback'),
    path('sso/logout/', sso_views.eve_logout, name="eve_logout"),
    path('', web_views.index, name="main"),
    path('auth/dashboard/', web_views.dashboard, name="dashboard")
]
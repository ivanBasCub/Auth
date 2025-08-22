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
    path('auth/dashboard/', web_views.dashboard, name="dashboard"),
    path('auth/audit/', web_views.audit_account, name="audit"),
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
]
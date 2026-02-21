from django.urls import path
from . import views

urlpatterns = [
    # Doctrines
    # User views
    path('list/', views.list_doctrines, name="List of doctrines"),
    path('<int:doc_id>/', views.doctrine_info, name="Doctrine info"),
    # Admin views
    path('admin/', views.admin_doctrines, name="Administrate doctrines"),
    path('admin/doctrine/add/', views.add_doctrine, name="Create a new doctrine"),
    path('admin/doctrine/edit/<int:doctrine_id>/', views.edit_doctrine, name="Edit a doctrine"),
    path('admin/doctrine/del/<int:doctrine_id>/', views.del_doctrine, name="Delete a doctrine"),
    path('admin/category/add/', views.add_doctrine_category, name="Add new doctrine category"),
    path('admin/category/edit/<int:category_id>', views.edit_doctrine_category, name="Add new doctrine category"),
    path('admin/category/del/<int:category_id>', views.del_doctrine_category, name="Add new doctrine category"),
    # Fits
    path('fit/<int:fit_id>/', views.fit, name="View fit info"),
    path('fit/edit/<int:fit_id>/', views.edit_fit, name="Edit fit info")
]
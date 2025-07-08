from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('change-password/', views.change_password, name='change_password'),
    path('verify/<uuid:token>/', views.verify_email, name='verify_email'),
    
    # Admin URLs
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin/user/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin/user/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),
]

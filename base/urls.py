from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('profile/<int:pk>/', views.profile, name='profile'),
    path('signup/',views.signup, name='signup' ),
    path('signin/',views.signin, name='signin' ),
    path('profile_delete<int:pk>/',views.profile_delete, name='profile_delete' ),
    path('profile_edit<int:pk>/',views.profile_edit, name='profile_edit' ),
     
    path('verify_email/<int:user_id>/<str:token>/', views.verify_email, name='verify_email'),
    path('verification-success/', views.verification_success, name='verification_success'),
    path('verification-failed/', views.verification_failed, name='verification_failed'),
    path('resend_verification/', views.verification_failed, name='resend_verification'),

]
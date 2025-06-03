# users/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication URLs
    # ------------------
    # Login/Logout - accessible to all users
    path('login/', views.UserLoginView.as_view(), name='login'),
    
    # Use Django's built-in LogoutView with proper configuration
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    
    # Rest of your URLs remain the same...
    path('password-change/', views.UserPasswordChangeView.as_view(), name='password-change'),
    path('password-change/done/', views.PasswordChangeDoneView.as_view(), name='password-change-done'),
    path('users/password-display/', views.UserPasswordDisplayView.as_view(), name='user-password-display'),

    # Password reset - accessible to anonymous users
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html',
        email_template_name='users/password_reset_email.html',
        subject_template_name='users/password_reset_subject.txt',
        success_url=reverse_lazy('users:password-reset-done')
    ), name='password-reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'
    ), name='password-reset-done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html',
        success_url=reverse_lazy('users:password-reset-complete')
    ), name='password-reset-confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password-reset-complete'),
    
    # Registration - accessible only to headmasters
    path('register/', views.UserCreateView.as_view(), name='register'),
    
    # Dashboard - accessible to logged-in users
    # ------------------
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # User Management - accessible only to headmasters
    # ------------------
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/create/', views.UserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/update/', views.UserUpdateView.as_view(), name='user-update'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user-delete'),
    path('users/<int:pk>/reset-password/', views.UserResetPasswordView.as_view(), name='user-reset-password'),

    # Other views
    # ------------------
    path('coming-soon/', views.ComingSoonView.as_view(), name='coming-soon'),
]
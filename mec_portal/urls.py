# mec_portal/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.shortcuts import redirect


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('users:login'), name='root'),
    # Single entry point for all user-related URLs
    path('', include('users.urls')),
    path('attendance/', include('attendance.urls')),
    path('lessonplans/', include('lessonplans.urls')),
    path('manifest.json', TemplateView.as_view(
        template_name='manifest.json', 
        content_type='application/json'
    )),
    path("__reload__/", include("django_browser_reload.urls")),
    path('', include('pwa.urls')),
]

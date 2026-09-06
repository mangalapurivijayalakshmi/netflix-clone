"""
URL configuration for Netflix_Clone project.

The `urlpatterns` list routes URLs to views.
For more information please see:
https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('app.api_urls')),
    # Language Switch URL
    path('i18n/', include('django.conf.urls.i18n')),

    # App URLs
    path('', include('app.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
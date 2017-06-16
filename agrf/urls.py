"""agrf URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
"""
from django.conf.urls import url, include
from django.contrib import admin

admin.site.site_header = 'AGRF Data Importer'
admin.site.site_title = 'AGRF'

urlpatterns = [
    url(r'^uom_admin/', admin.site.urls, name='admin'),
    # Add Django site authentication urls (for login, logout, etc...)
    url(r'^accounts/', include('django.contrib.auth.urls')),
    # Our agrf application
    url(r'', include('agrf_feed.urls', namespace='agrf'))
]

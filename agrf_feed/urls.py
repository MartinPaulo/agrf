from django.conf.urls import url

from agrf_feed import views

app_name = 'agrf'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^files$', views.files, name='files'),
    url(r'^target_selector$', views.target_selector, name='target_selector'),
    url(r'^gs_logout$', views.gs_logout, name='gs_logout'),
    url(r'^gs_login/$', views.gs_login, name='gs_login')
]

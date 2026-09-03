from django.urls import path
from . import views

app_name = 'vpn_panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('save-config/', views.save_config, name='save_config'),
    path('toggle-connection/', views.toggle_connection, name='toggle_connection'),
]

from django.urls import path
from . import views

app_name = 'vpn_panel'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('config/add/', views.ConfigCreateView.as_view(), name='config_add'),
    path('config/<int:pk>/edit/', views.ConfigUpdateView.as_view(), name='config_edit'),
    path('config/<int:pk>/delete/', views.ConfigDeleteView.as_view(), name='config_delete'),
    path('config/<int:pk>/toggle/', views.ToggleConnectionView.as_view(), name='config_toggle'),
    path('config/<int:pk>/ping/', views.PingCheckView.as_view(), name='config_ping'),
    path('logs/', views.LogsView.as_view(), name='logs'),
]

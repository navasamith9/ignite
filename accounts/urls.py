from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # The main entry point is now handled by allauth (Google)
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
]
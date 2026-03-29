from django.urls import path
from . import views

app_name = 'helpdesk'

urlpatterns = [
    path('', views.chat_page, name='chat'),
    path('api/chat/', views.chat_api, name='chat_api'),
]
from django.urls import path
from . import views

app_name = 'lhtc'

urlpatterns = [
    path('rooms/', views.room_list_view, name='room_list'),
    path('bookings/', views.booking_list_view, name='booking_list'),
    path('create/', views.create_booking_view, name='create_booking'),
    path('edit/<uuid:booking_id>/', views.edit_booking_view, name='edit_booking'),
    path('cancel/<uuid:booking_id>/', views.cancel_booking_view, name='cancel_booking'),
    path('ai-recommend/', views.ai_recommendation_view, name='ai_recommendation'),
    path('register/<uuid:booking_id>/', views.register_for_event, name='register_event'),
]
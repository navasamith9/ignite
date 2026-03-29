from django.urls import path
from . import views

app_name = 'bus'

urlpatterns = [
    path('routes/', views.bus_list_view, name='bus_list'),

    # ✅ ONLY ONE booking route (use this everywhere)
    path('book/<uuid:route_id>/', views.book_bus_view, name='book'),

    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('cancel/<uuid:booking_id>/', views.cancel_booking_view, name='cancel_booking'),
    path('details/<uuid:booking_id>/', views.booking_details_view, name='booking_details'),
    path('download/<uuid:booking_id>/', views.download_ticket_view, name='download_ticket'),

    # ✅ FIXED UUID
    path('payment/<uuid:booking_id>/', views.payment_view, name='payment'),
    path('qr/<uuid:booking_id>/', views.generate_qr_view, name='qr'),
]
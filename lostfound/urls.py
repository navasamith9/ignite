from django.urls import path
from . import views

app_name = 'lostfound'

urlpatterns = [
    path('lost/', views.lost_items_view, name='lost_items'),
    path('found/', views.found_items_view, name='found_items'),
    path('report-lost/', views.report_lost_view, name='report_lost'),
    path('report-found/', views.report_found_view, name='report_found'),
    path('item/<uuid:item_id>/<str:item_type>/', views.item_detail_view, name='item_detail'),
]
from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('menu/', views.menu_view, name='menu'),
    path('kitchen/', views.kitchen_view, name='kitchen'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('qr-codes/', views.qr_codes_view, name='qr_codes'),
    # APIs
    path('api/menu/', views.api_menu, name='api_menu'),
    path('api/orders/', views.api_orders, name='api_orders'),
    path('api/orders/place/', views.api_place_order, name='api_place_order'),
    path('api/orders/<int:order_id>/status/', views.api_update_order_status, name='api_update_status'),
    path('api/tables/', views.api_tables, name='api_tables'),
    path('api/generate-qr/<int:table_number>/', views.generate_qr, name='generate_qr'),
    path('api/payment/cash/<int:order_id>/', views.cash_payment, name='cash_payment'),
]

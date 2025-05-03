from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .custom_login_view import SessionControlLoginView

urlpatterns = [
    # Dashboard and authentication
    path('', views.dashboard, name='dashboard'),
    path('login/', SessionControlLoginView.as_view(template_name='workflow/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='workflow/logout.html'), name='logout'),
    
    # Products
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/new/', views.ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
    
    # Units
    path('units/', views.UnitListView.as_view(), name='unit-list'),
    path('units/new/', views.UnitCreateView.as_view(), name='unit-create'),
    path('units/<int:pk>/update/', views.UnitUpdateView.as_view(), name='unit-update'),
    path('units/<int:pk>/delete/', views.UnitDeleteView.as_view(), name='unit-delete'),
    
    # Drivers
    path('drivers/', views.DriverListView.as_view(), name='driver-list'),
    path('drivers/add/', views.DriverCreateView.as_view(), name='driver-create'),
    path('drivers/<int:pk>/update/', views.DriverUpdateView.as_view(), name='driver-update'),
    path('drivers/<int:pk>/delete/', views.DriverDeleteView.as_view(), name='driver-delete'),
    
    # Orders
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/new/', views.create_order, name='order-create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/approve/', views.approve_order, name='order-approve'),
    path('orders/<int:pk>/reject/', views.reject_order, name='order-reject'),
    path('orders/<int:pk>/deliver/', views.mark_delivered, name='order-deliver'),
    path('orders/<int:pk>/confirm-receipt/', views.confirm_receipt, name='order-confirm-receipt'),
    path('orders/<int:pk>/edit/', views.edit_order_items, name='order-edit'),
    path('orders/<int:pk>/edit-prices/', views.edit_order_prices, name='order-edit-prices'),
    path('orders/<int:pk>/invoice/', views.generate_invoice_pdf, name='generate-invoice'),
    
    # Reports
    path('reports/', views.reports_dashboard, name='reports-dashboard'),
    path('reports/orders/', views.orders_report, name='orders-report'),
    path('reports/delivery/', views.delivery_report, name='delivery-report'),
    path('reports/financial/', views.financial_report, name='financial-report'),
    
    # API endpoints
    path('products/api/get-product-info/', views.get_product_info, name='get-product-info'),
] 
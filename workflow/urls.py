from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Dashboard and authentication
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='workflow/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='workflow/logout.html'), name='logout'),
    
    # Products
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/new/', views.ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    
    # Drivers
    path('drivers/', views.DriverListView.as_view(), name='driver-list'),
    path('drivers/new/', views.DriverCreateView.as_view(), name='driver-create'),
    path('drivers/<int:pk>/update/', views.DriverUpdateView.as_view(), name='driver-update'),
    
    # Orders
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/new/', views.create_order, name='order-create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/approve/', views.approve_order, name='order-approve'),
    path('orders/<int:pk>/reject/', views.reject_order, name='order-reject'),
    path('orders/<int:pk>/deliver/', views.mark_delivered, name='order-deliver'),
    path('orders/<int:pk>/confirm-receipt/', views.confirm_receipt, name='order-confirm-receipt'),
    path('orders/<int:pk>/invoice/', views.generate_invoice_pdf, name='order-invoice'),
    
    # Reports
    path('reports/', views.reports_dashboard, name='reports-dashboard'),
    path('reports/orders/', views.order_report, name='order-report'),
] 
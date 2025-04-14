from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.forms import modelformset_factory
from django.http import HttpResponseForbidden, HttpResponse
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.db import transaction
import decimal
from django.db.models import Q

from .models import User, Product, Order, OrderItem, Driver, Unit
from .forms import (
    UserRegisterForm, ProductForm, OrderItemForm, OrderItemFormSet, 
    WarehouseOrderForm, WarehouseOrderItemForm, OrderReceiptForm, DriverForm,
    UnitForm
)

# Utility functions
def role_required(roles):
    """Decorator to restrict view access based on user roles"""
    def decorator(view_func):
        @login_required
        def wrapped_view(request, *args, **kwargs):
            if request.user.role in roles:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You don't have permission to access this page.")
        return wrapped_view
    return decorator

# Authentication views
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'workflow/register.html', {'form': form})

# Product views
class ProductListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Product
    template_name = 'workflow/product_list.html'
    context_object_name = 'products'
    ordering = ['title']
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(code__icontains=query)
            )
        
        return queryset
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'WAREHOUSE', 'ACCOUNTANT']

class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'workflow/product_form.html'
    success_url = reverse_lazy('product-list')
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'WAREHOUSE']
    
    def form_valid(self, form):
        messages.success(self.request, f'Product created successfully!')
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'workflow/product_form.html'
    success_url = reverse_lazy('product-list')
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'WAREHOUSE']
    
    def form_valid(self, form):
        messages.success(self.request, f'Product updated successfully!')
        return super().form_valid(form)

class ProductDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Product
    template_name = 'workflow/product_detail.html'
    context_object_name = 'product'
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'WAREHOUSE', 'ACCOUNTANT']

class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'workflow/product_confirm_delete.html'
    success_url = reverse_lazy('product-list')
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'WAREHOUSE']
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'محصول با موفقیت حذف شد.')
        return super().delete(request, *args, **kwargs)

# Driver views
class DriverListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Driver
    template_name = 'workflow/driver_list.html'
    context_object_name = 'drivers'
    ordering = ['name']
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | 
                Q(phone__icontains=query) | 
                Q(license_plate__icontains=query)
            )
        
        return queryset
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'WAREHOUSE']

class DriverCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Driver
    form_class = DriverForm
    template_name = 'workflow/driver_form.html'
    success_url = reverse_lazy('driver-list')
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'WAREHOUSE']
    
    def form_valid(self, form):
        messages.success(self.request, f'Driver created successfully!')
        return super().form_valid(form)

class DriverUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Driver
    form_class = DriverForm
    template_name = 'workflow/driver_form.html'
    success_url = reverse_lazy('driver-list')
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'WAREHOUSE']
    
    def form_valid(self, form):
        messages.success(self.request, f'Driver updated successfully!')
        return super().form_valid(form)

# Order views
@login_required
def dashboard(request):
    user = request.user
    context = {
        'user': user,
    }
    
    if user.role == 'REQUESTER':
        context['pending_orders'] = Order.objects.filter(requester=user, status='PENDING').count()
        context['approved_orders'] = Order.objects.filter(requester=user, status='APPROVED').count()
        context['delivered_orders'] = Order.objects.filter(requester=user, status='DELIVERED').count()
        context['recent_orders'] = Order.objects.filter(requester=user).order_by('-order_date')[:5]
    
    elif user.role == 'WAREHOUSE':
        context['pending_approvals'] = Order.objects.filter(status='PENDING').count()
        context['approved_orders'] = Order.objects.filter(status='APPROVED').count()
        context['recent_orders'] = Order.objects.all().order_by('-order_date')[:5]
    
    elif user.role == 'ACCOUNTANT' or user.role == 'ADMIN':
        context['total_orders'] = Order.objects.count()
        context['received_orders'] = Order.objects.filter(status='RECEIVED').count()
        context['recent_orders'] = Order.objects.all().order_by('-order_date')[:5]
    
    return render(request, 'workflow/dashboard.html', context)

@login_required
def create_order(request):
    if request.user.role != 'REQUESTER':
        return HttpResponseForbidden("Only requesters can create orders")
    
    OrderItemFormSet = modelformset_factory(
        OrderItem, 
        form=OrderItemForm,
        min_num=1, 
        extra=0, 
        can_delete=True
    )
    
    if request.method == 'POST':
        formset = OrderItemFormSet(request.POST, queryset=OrderItem.objects.none())
        
        if formset.is_valid():
            with transaction.atomic():
                order = Order.objects.create(requester=request.user)
                
                for form in formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        item = form.save(commit=False)
                        item.order = order
                        item.save()
                
                messages.success(request, 'Order created successfully!')
                return redirect('order-detail', pk=order.pk)
        else:
            messages.error(request, 'There was an error in your order. Please check the form.')
    else:
        formset = OrderItemFormSet(queryset=OrderItem.objects.none())
        # Add at least one empty form
        if not formset.forms:
            formset = OrderItemFormSet(queryset=OrderItem.objects.none(), initial=[{'requested_quantity': 1}])
    
    return render(request, 'workflow/order_form.html', {
        'formset': formset,
        'products': Product.objects.all(),
    })

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'workflow/order_list.html'
    context_object_name = 'orders'
    ordering = ['-order_date']
    
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.role == 'REQUESTER':
            return queryset.filter(requester=user)
        elif user.role == 'WAREHOUSE':
            return queryset
        elif user.role == 'ACCOUNTANT':
            return queryset
        
        return queryset

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'workflow/order_detail.html'
    context_object_name = 'order'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        
        # For warehouse manager
        if self.request.user.role == 'WAREHOUSE':
            # Add drivers to context for all warehouse managers regardless of status
            context['drivers'] = Driver.objects.all()
            
            if self.object.status == 'PENDING':
                context['warehouse_form'] = WarehouseOrderForm(instance=self.object)
                context['can_approve'] = True
        
        # For requester
        if self.request.user.role == 'REQUESTER' and self.object.status == 'DELIVERED':
            context['receipt_form'] = OrderReceiptForm(instance=self.object)
            context['can_confirm_receipt'] = True
            
        return context

@role_required(['WAREHOUSE'])
def approve_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if order.status != 'PENDING':
        messages.error(request, 'این سفارش نمی‌تواند تایید شود زیرا در وضعیت انتظار نیست.')
        return redirect('order-detail', pk=order.pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            with transaction.atomic():
                # Update each item's approved quantity
                for item in order.items.all():
                    item_quantity = request.POST.get(f'item_{item.id}')
                    if item_quantity:
                        try:
                            item.approved_quantity = decimal.Decimal(item_quantity)
                            item.save()
                        except decimal.InvalidOperation:
                            messages.error(request, f'مقدار نامعتبر برای {item.product.title}')
                            return redirect('order-detail', pk=order.pk)
                
                # Add notes if provided
                notes = request.POST.get('notes')
                if notes:
                    order.notes = notes
                
                # Mark as approved
                order.approve(request.user)
                
                messages.success(request, 'سفارش با موفقیت تایید شد!')
        
        elif action == 'reject':
            notes = request.POST.get('notes', '')
            order.reject(request.user, notes)
            messages.success(request, 'سفارش با موفقیت رد شد.')
    
    return redirect('order-detail', pk=order.pk)

@role_required(['WAREHOUSE'])
def reject_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if order.status != 'PENDING':
        messages.error(request, 'This order cannot be rejected because it is not pending.')
        return redirect('order-detail', pk=order.pk)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        order.reject(request.user, reason)
        messages.success(request, 'Order rejected successfully.')
    
    return redirect('order-detail', pk=order.pk)

@role_required(['WAREHOUSE'])
def mark_delivered(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if order.status != 'APPROVED':
        messages.error(request, 'This order cannot be marked as delivered because it is not approved.')
        return redirect('order-detail', pk=order.pk)
    
    if request.method == 'POST':
        driver_id = request.POST.get('driver')
        driver = None
        if driver_id:
            driver = get_object_or_404(Driver, pk=driver_id)
        
        order.mark_delivered(driver)
        messages.success(request, 'Order marked as delivered successfully.')
    
    return redirect('order-detail', pk=order.pk)

@role_required(['REQUESTER'])
def confirm_receipt(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if request.user != order.requester:
        return HttpResponseForbidden("You don't have permission to confirm this order.")
    
    if order.status != 'DELIVERED':
        messages.error(request, 'This order cannot be confirmed because it is not marked as delivered.')
        return redirect('order-detail', pk=order.pk)
    
    if request.method == 'POST':
        form = OrderReceiptForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            order.mark_received()
            messages.success(request, 'Order confirmed as received successfully.')
        else:
            messages.error(request, 'There was an error in the form.')
    
    return redirect('order-detail', pk=order.pk)

# Report views
@login_required
def reports_dashboard(request):
    """Dashboard showing all reports and statistics"""
    # Get counts for dashboard statistics
    context = {
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
        'total_users': User.objects.count(),
        'total_drivers': Driver.objects.count(),
        
        # Order counts by status
        'pending_orders': Order.objects.filter(status='PENDING').count(),
        'approved_orders': Order.objects.filter(status='APPROVED').count(),
        'ready_orders': Order.objects.filter(status='READY').count(),
        'shipping_orders': Order.objects.filter(status='SHIPPING').count(),
        'delivered_orders': Order.objects.filter(status='DELIVERED').count(),
        'cancelled_orders': Order.objects.filter(status='CANCELLED').count(),
    }
    return render(request, 'workflow/reports_dashboard.html', context)

@login_required
def orders_report(request):
    """Report showing order statistics"""
    # Get date filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status')
    
    orders = Order.objects.all()
    
    # Apply filters if provided
    if start_date:
        orders = orders.filter(created_at__gte=start_date)
    if end_date:
        orders = orders.filter(created_at__lte=end_date)
    if status:
        orders = orders.filter(status=status)
    
    # Calculate total revenue
    total_revenue = sum(order.total_price for order in orders if hasattr(order, 'total_price'))
    
    # Count orders by status
    delivered_count = sum(1 for order in orders if order.status in ['DELIVERED', 'RECEIVED'])
    processing_count = sum(1 for order in orders if order.status in ['PENDING', 'APPROVED', 'READY', 'SHIPPING'])
    rejected_count = sum(1 for order in orders if order.status in ['REJECTED', 'CANCELLED'])
    
    # Analyze branches with most orders
    branches = {}
    for order in orders:
        branch_name = order.requester.branch_name if hasattr(order.requester, 'branch_name') and order.requester.branch_name else 'نامشخص'
        if branch_name not in branches:
            branches[branch_name] = {'order_count': 0, 'total_amount': 0}
        
        branches[branch_name]['order_count'] += 1
        branches[branch_name]['total_amount'] += order.total_price if hasattr(order, 'total_price') else 0
    
    # Convert to list and sort by order count
    top_branches = [{'branch_name': name, 'order_count': data['order_count'], 'total_amount': data['total_amount']} 
                   for name, data in branches.items()]
    top_branches = sorted(top_branches, key=lambda x: x['order_count'], reverse=True)[:5]
    
    context = {
        'orders': orders,
        'start_date': start_date,
        'end_date': end_date,
        'status': status,
        'status_choices': Order.STATUS_CHOICES,
        'total_revenue': total_revenue,
        'delivered_count': delivered_count,
        'processing_count': processing_count,
        'rejected_count': rejected_count,
        'top_branches': top_branches,
    }
    return render(request, 'workflow/orders_report.html', context)

@login_required
def delivery_report(request):
    """Report showing delivery statistics by driver"""
    drivers = Driver.objects.all()
    
    driver_stats = []
    for driver in drivers:
        driver_orders = Order.objects.filter(driver=driver)
        total_orders = driver_orders.count()
        delivered_orders = driver_orders.filter(status='DELIVERED').count()
        pending_orders = driver_orders.filter(status='SHIPPING').count()
        
        driver_stats.append({
            'driver': driver,
            'total_orders': total_orders,
            'delivered_orders': delivered_orders,
            'pending_orders': pending_orders
        })
    
    context = {
        'driver_stats': driver_stats
    }
    return render(request, 'workflow/delivery_report.html', context)

@login_required
def financial_report(request):
    """Report showing financial statistics"""
    # Get date filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    orders = Order.objects.filter(status='DELIVERED')
    
    # Apply date filters if provided
    if start_date:
        orders = orders.filter(delivered_at__gte=start_date)
    if end_date:
        orders = orders.filter(delivered_at__lte=end_date)
    
    # Calculate total revenue
    total_revenue = sum(order.total_price for order in orders if hasattr(order, 'total_price'))
    
    # Group by month for chart
    monthly_revenue = {}
    for order in orders:
        if order.delivered_at:  # Check if delivered_at is not None
            month_year = order.delivered_at.strftime('%Y-%m')
            if month_year in monthly_revenue:
                monthly_revenue[month_year] += order.total_price
            else:
                monthly_revenue[month_year] = order.total_price
    
    # Sort monthly revenue by date for better display
    monthly_revenue = dict(sorted(monthly_revenue.items()))
    
    context = {
        'orders': orders,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'workflow/financial_report.html', context)

@login_required
def generate_invoice_pdf(request, pk):
    """Generate a PDF invoice for an order"""
    order = get_object_or_404(Order, pk=pk)
    
    # In a production environment, you would use a library like ReportLab or WeasyPrint
    # to generate a proper PDF invoice
    
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.txt"'
    
    # تابع کمکی برای فرمت کردن قیمت‌ها
    def format_price(value):
        if value is None:
            return ""
        
        try:
            # تبدیل به Decimal برای اطمینان
            decimal_value = decimal.Decimal(str(value))
            
            # اگر عدد صحیح است، فقط بخش صحیح را برگردان
            if decimal_value == decimal_value.to_integral_value():
                return int(decimal_value)
            
            # در غیر این صورت، عدد اعشاری را برگردان، با حذف صفرهای انتهایی
            return str(decimal_value).rstrip('0').rstrip('.') if '.' in str(decimal_value) else decimal_value
        except:
            return value
    
    lines = [
        f"INVOICE #{order.id}",
        f"Date: {order.order_date.strftime('%Y-%m-%d')}",
        f"Requester: {order.requester.get_full_name() or order.requester.username}",
        f"Status: {order.get_status_display()}",
        f"Driver: {order.driver.name if order.driver else 'Not assigned'}",
        "",
        "ITEMS:",
        "----------------------------------------------",
        "Product | Quantity | Unit | Price | Total",
        "----------------------------------------------",
    ]
    
    total_price = 0
    for item in order.items.all():
        price = item.price_per_unit or 0
        qty = item.approved_quantity or item.requested_quantity
        total = price * qty
        total_price += total
        
        lines.append(f"{item.product.title} ({item.product.code}) | {format_price(qty)} | {item.product.unit} | {format_price(price)} | {format_price(total)}")
    
    lines.extend([
        "----------------------------------------------",
        f"TOTAL: {format_price(total_price)}",
        "",
        f"Notes: {order.notes or 'N/A'}"
    ])
    
    response.write('\n'.join(lines))
    return response

# Unit views
class UnitListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Unit
    template_name = 'workflow/unit_list.html'
    context_object_name = 'units'
    ordering = ['name']
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | 
                Q(symbol__icontains=query)
            )
        
        return queryset
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'WAREHOUSE']

class UnitCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Unit
    form_class = UnitForm
    template_name = 'workflow/unit_form.html'
    success_url = reverse_lazy('unit-list')
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'WAREHOUSE']
    
    def form_valid(self, form):
        messages.success(self.request, 'واحد با موفقیت ایجاد شد!')
        return super().form_valid(form)

class UnitUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Unit
    form_class = UnitForm
    template_name = 'workflow/unit_form.html'
    success_url = reverse_lazy('unit-list')
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'WAREHOUSE']
    
    def form_valid(self, form):
        messages.success(self.request, 'واحد با موفقیت به‌روزرسانی شد!')
        return super().form_valid(form)

class UnitDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Unit
    template_name = 'workflow/unit_confirm_delete.html'
    success_url = reverse_lazy('unit-list')
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'WAREHOUSE']
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'واحد با موفقیت حذف شد.')
        return super().delete(request, *args, **kwargs)

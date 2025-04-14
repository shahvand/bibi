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

from .models import User, Product, Order, OrderItem, Driver
from .forms import (
    UserRegisterForm, ProductForm, OrderItemForm, OrderItemFormSet, 
    WarehouseOrderForm, WarehouseOrderItemForm, OrderReceiptForm, DriverForm
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

# Driver views
class DriverListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Driver
    template_name = 'workflow/driver_list.html'
    context_object_name = 'drivers'
    ordering = ['name']
    
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
        if self.request.user.role == 'WAREHOUSE' and self.object.status == 'PENDING':
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
        messages.error(request, 'This order cannot be approved because it is not pending.')
        return redirect('order-detail', pk=order.pk)
    
    if request.method == 'POST':
        order_form = WarehouseOrderForm(request.POST, instance=order)
        items_data = []
        
        for item in order.items.all():
            item_prefix = f'item_{item.id}'
            item_data = {
                'approved_quantity': request.POST.get(f'{item_prefix}_approved_quantity', item.requested_quantity),
                'price_per_unit': request.POST.get(f'{item_prefix}_price_per_unit', item.product.price_per_unit),
                'notes': request.POST.get(f'{item_prefix}_notes', ''),
            }
            items_data.append((item, item_data))
        
        if order_form.is_valid():
            with transaction.atomic():
                # Save the main order form
                order_form.save()
                
                # Update each item
                for item, item_data in items_data:
                    item.approved_quantity = item_data['approved_quantity']
                    item.price_per_unit = item_data['price_per_unit']
                    item.notes = item_data['notes']
                    item.save()
                
                # Mark as approved
                order.approve(request.user)
                
                messages.success(request, 'Order approved successfully!')
                return redirect('order-detail', pk=order.pk)
        else:
            messages.error(request, 'There was an error in the form. Please check the data.')
    
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
@role_required(['ACCOUNTANT', 'ADMIN'])
def reports_dashboard(request):
    today = timezone.now().date()
    
    context = {
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='PENDING').count(),
        'approved_orders': Order.objects.filter(status='APPROVED').count(),
        'delivered_orders': Order.objects.filter(status='DELIVERED').count(),
        'received_orders': Order.objects.filter(status='RECEIVED').count(),
        'today_orders': Order.objects.filter(order_date__date=today).count(),
    }
    
    return render(request, 'workflow/reports_dashboard.html', context)

@role_required(['ACCOUNTANT', 'ADMIN'])
def order_report(request):
    orders = Order.objects.all().order_by('-order_date')
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # Filter by date range if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        orders = orders.filter(order_date__date__gte=start_date)
    
    if end_date:
        orders = orders.filter(order_date__date__lte=end_date)
    
    # Filter by requester if provided
    requester = request.GET.get('requester')
    if requester:
        orders = orders.filter(requester__id=requester)
    
    return render(request, 'workflow/order_report.html', {
        'orders': orders,
        'requesters': User.objects.filter(role='REQUESTER'),
        'status_choices': Order.STATUS_CHOICES,
    })

@role_required(['ACCOUNTANT', 'ADMIN', 'WAREHOUSE'])
def generate_invoice_pdf(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    # Create a simple HTTP response for now
    # In a production environment, you would use a library like ReportLab or WeasyPrint
    # to generate a proper PDF invoice
    
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.txt"'
    
    lines = [
        f"INVOICE #{order.id}",
        f"Date: {order.order_date.strftime('%Y-%m-%d')}",
        f"Requester: {order.requester.get_full_name() or order.requester.username}",
        f"Branch: {order.requester.branch_name or 'N/A'}",
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
        
        lines.append(f"{item.product.title} ({item.product.code}) | {qty} | {item.product.unit} | {price} | {total}")
    
    lines.extend([
        "----------------------------------------------",
        f"TOTAL: {total_price}",
        "",
        f"Notes: {order.notes or 'N/A'}"
    ])
    
    response.write('\n'.join(lines))
    return response

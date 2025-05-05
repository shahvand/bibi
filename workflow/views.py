from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.forms import modelformset_factory, inlineformset_factory, forms
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.db import transaction
import decimal
from django.db.models import Q
from .templatetags.workflow_filters import format_price

from .models import User, Product, Order, OrderItem, Driver, Unit
from .forms import (
    UserRegisterForm, ProductForm, OrderItemForm, OrderItemFormSet, 
    WarehouseOrderForm, WarehouseOrderItemForm, OrderReceiptForm, DriverForm,
    UnitForm, RequesterOrderEditForm, OrderItemEditForm
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
        return self.request.user.role in ['ADMIN', 'ACCOUNTANT']
    
    def form_valid(self, form):
        messages.success(self.request, f'کالا با موفقیت ایجاد شد!')
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'workflow/product_form.html'
    success_url = reverse_lazy('product-list')
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'ACCOUNTANT']
    
    def form_valid(self, form):
        messages.success(self.request, f'کالا با موفقیت به‌روزرسانی شد!')
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
        return self.request.user.role in ['ADMIN', 'ACCOUNTANT']
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'کالا با موفقیت حذف شد.')
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
        messages.success(self.request, 'راننده با موفقیت به‌روزرسانی شد!')
        return super().form_valid(form)

class DriverDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Driver
    template_name = 'workflow/driver_confirm_delete.html'
    success_url = reverse_lazy('driver-list')
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'WAREHOUSE']
    
    def delete(self, request, *args, **kwargs):
        driver = self.get_object()
        # اگر راننده با سفارشی مرتبط است، اجازه حذف نمی‌دهیم
        if driver.order_set.exists():
            messages.error(request, 'این راننده با سفارش‌هایی مرتبط است و نمی‌توان آن را حذف کرد.')
            return HttpResponseRedirect(self.success_url)
        
        messages.success(request, 'راننده با موفقیت حذف شد.')
        return super().delete(request, *args, **kwargs)

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
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # فیلتر بر اساس نقش کاربر
        if user.role == 'REQUESTER':
            queryset = queryset.filter(requester=user)
        
        # فیلتر بر اساس وضعیت سفارش
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # فیلتر بر اساس تاریخ
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(order_date__gte=date_from)
            
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(order_date__lte=date_to)
        
        # فیلتر بر اساس جستجو
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(id__icontains=search) |
                Q(requester__username__icontains=search) |
                Q(requester__first_name__icontains=search) |
                Q(requester__last_name__icontains=search) |
                Q(notes__icontains=search)
            )
        
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
        if self.request.user.role == 'REQUESTER' and self.request.user == self.object.requester:
            # امکان تایید دریافت در وضعیت تحویل راننده شده
            if self.object.status == 'DELIVERED':
                context['receipt_form'] = OrderReceiptForm(instance=self.object)
                context['can_confirm_receipt'] = True
            
            # امکان ویرایش در حالت‌های زیر:
            # 1. در وضعیت PENDING، همیشه قابل ویرایش است
            # 2. در وضعیت APPROVED، فقط اگر به راننده تحویل داده نشده باشد
            if self.object.status == 'PENDING' or (self.object.status == 'APPROVED' and self.object.driver is None):
                context['can_edit_order'] = True
                context['edit_form'] = RequesterOrderEditForm(instance=self.object)
        
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
                            # Parse the input to Decimal
                            quantity = decimal.Decimal(item_quantity)
                            
                            # Validate that the number isn't too large for the database field
                            # Max digits is 15, so the number must be less than 10^15
                            if quantity >= decimal.Decimal('1000000000000000'):  # 10^15
                                messages.error(
                                    request, 
                                    f'مقدار بیش از حد مجاز برای {item.product.title}. حداکثر مقدار مجاز ۹۹۹,۹۹۹,۹۹۹,۹۹۹,۹۹۹ می‌باشد.'
                                )
                                return redirect('order-detail', pk=order.pk)
                            
                            # Validate that the number isn't negative
                            if quantity < 0:
                                messages.error(
                                    request, 
                                    f'مقدار نمی‌تواند منفی باشد برای {item.product.title}'
                                )
                                return redirect('order-detail', pk=order.pk)
                            
                            item.approved_quantity = quantity
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

@login_required
@role_required(['REQUESTER'])
def edit_order_items(request, pk):
    """ویرایش آیتم‌های سفارش توسط درخواست کننده"""
    order = get_object_or_404(Order, pk=pk)
    
    # بررسی دسترسی: فقط درخواست کننده خود سفارش می‌تواند آن را ویرایش کند
    if request.user != order.requester:
        return HttpResponseForbidden("شما اجازه ویرایش این سفارش را ندارید.")
    
    # بررسی وضعیت: 
    # 1. در حالت PENDING کاربر می‌تواند سفارش را ویرایش کند
    # 2. در حالت APPROVED فقط اگر به راننده تحویل داده نشده باشد، قابل ویرایش است
    # 3. در سایر حالت‌ها امکان ویرایش وجود ندارد
    if order.status not in ['PENDING', 'APPROVED']:
        messages.error(request, 'این سفارش در وضعیتی نیست که بتوانید آن را ویرایش کنید.')
        return redirect('order-detail', pk=order.pk)
    
    if order.status == 'APPROVED' and order.driver is not None:
        messages.error(request, 'این سفارش به راننده تحویل شده و دیگر قابل ویرایش نیست.')
        return redirect('order-detail', pk=order.pk)
    
    # تنظیم فرم‌ست برای آیتم‌های سفارش - امکان اضافه و حذف آیتم فقط در حالت PENDING
    can_add_remove = order.status == 'PENDING'
    OrderItemFormSet = inlineformset_factory(
        Order, OrderItem, 
        form=OrderItemEditForm,
        extra=1,  # همیشه یک ردیف خالی برای اضافه کردن
        can_delete=can_add_remove
    )
    
    if request.method == 'POST':
        order_form = RequesterOrderEditForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)
        
        if order_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                # ذخیره یادداشت‌های سفارش
                order_form.save()
                
                # ذخیره تغییرات آیتم‌ها با بررسی آیتم‌های رد شده
                formset.save()
                
                # در حالت PENDING نیازی به بررسی رد شدن نیست
                if order.status == 'APPROVED':
                    # بررسی اگر تمام آیتم‌ها رد شده باشند، سفارش به وضعیت رد شده تغییر می‌کند
                    all_items_rejected = all(
                        item.approved_quantity == 0 
                        for item in order.items.all()
                    )
                    
                    if all_items_rejected:
                        order.status = 'REJECTED'
                        order.save()
                        messages.success(request, 'سفارش به دلیل رد تمام آیتم‌ها لغو شد.')
                
                messages.success(request, 'تغییرات سفارش با موفقیت ذخیره شد.')
                
            return redirect('order-detail', pk=order.pk)
        else:
            messages.error(request, 'لطفاً خطاهای فرم را اصلاح کنید.')
    else:
        order_form = RequesterOrderEditForm(instance=order)
        formset = OrderItemFormSet(instance=order)
    
    return render(request, 'workflow/order_edit.html', {
        'order': order,
        'order_form': order_form,
        'formset': formset,
        'can_add_remove': can_add_remove,
        'products': Product.objects.all().order_by('title'),
        'all_units': Unit.objects.all(),  # اضافه کردن تمام واحدهای اندازه‌گیری
    })

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
@role_required(['ACCOUNTANT', 'ADMIN'])
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
    # Check if user is accountant or admin
    if request.user.role not in ['ACCOUNTANT', 'ADMIN']:
        messages.error(request, 'شما دسترسی لازم برای مشاهده فاکتور را ندارید.')
        return redirect('dashboard')
        
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
    
    # تبدیل تاریخ میلادی به شمسی
    import jdatetime
    jalali_date = jdatetime.datetime.fromgregorian(datetime=order.order_date).strftime('%Y/%m/%d')
    
    lines = [
        f"INVOICE #{order.id}",
        f"Date: {jalali_date}",
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
        return self.request.user.role in ['ADMIN', 'WAREHOUSE', 'ACCOUNTANT']
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # فقط به حسابدار و ادمین اجازه افزودن واحد جدید داده می‌شود
        context['can_add_unit'] = self.request.user.role in ['ADMIN', 'ACCOUNTANT']
        # فقط به حسابدار و ادمین اجازه ویرایش و حذف واحدها داده می‌شود
        context['can_edit_unit'] = self.request.user.role in ['ADMIN', 'ACCOUNTANT']
        return context

class UnitCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Unit
    form_class = UnitForm
    template_name = 'workflow/unit_form.html'
    success_url = reverse_lazy('unit-list')
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'ACCOUNTANT']
    
    def form_valid(self, form):
        messages.success(self.request, 'واحد با موفقیت ایجاد شد!')
        return super().form_valid(form)

class UnitUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Unit
    form_class = UnitForm
    template_name = 'workflow/unit_form.html'
    success_url = reverse_lazy('unit-list')
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'ACCOUNTANT']
    
    def form_valid(self, form):
        messages.success(self.request, 'واحد با موفقیت به‌روزرسانی شد!')
        return super().form_valid(form)

class UnitDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Unit
    template_name = 'workflow/unit_confirm_delete.html'
    success_url = reverse_lazy('unit-list')
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'ACCOUNTANT']
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'واحد با موفقیت حذف شد.')
        return super().delete(request, *args, **kwargs)

@login_required
def get_product_info(request):
    """API برای دریافت اطلاعات کالا"""
    product_id = request.GET.get('id')
    if not product_id:
        return JsonResponse({'success': False, 'error': 'شناسه کالا ارسال نشده است'})
    
    try:
        product_id = int(product_id)
        
        # تهیه اطلاعات کالا
        product = Product.objects.get(pk=product_id)
        
        return JsonResponse({
            'success': True,
            'id': product.id,
            'title': product.title,
            'code': product.code,
            'unit': product.unit_ref.symbol if product.unit_ref else product.unit,
            'price': format_price(product.price_per_unit)
        })
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'کالا یافت نشد'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# ACCOUNTANT only views
@login_required
@role_required(['ACCOUNTANT', 'ADMIN'])
def edit_order_prices(request, pk):
    """ویرایش قیمت‌های محصولات در سفارش توسط حسابدار"""
    order = get_object_or_404(Order, pk=pk)
    
    # تنظیم فرم برای آیتم‌های سفارش با تمرکز بر فیلد قیمت
    class AccountantOrderItemForm(forms.ModelForm):
        class Meta:
            model = OrderItem
            fields = ['price_per_unit', 'notes']
            widgets = {
                'price_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
                'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            }
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if self.instance and self.instance.pk and self.instance.price_per_unit:
                self.initial['price_per_unit'] = format_price_input(self.instance.price_per_unit)
    
    OrderItemFormSet = inlineformset_factory(
        Order, OrderItem, 
        form=AccountantOrderItemForm,
        extra=0,
        can_delete=False
    )
    
    if request.method == 'POST':
        formset = OrderItemFormSet(request.POST, instance=order)
        
        if formset.is_valid():
            with transaction.atomic():
                formset.save()
                order.last_edit_time = timezone.now()
                order.save()
                messages.success(request, 'قیمت‌های سفارش با موفقیت به‌روزرسانی شدند.')
                return redirect('order-detail', pk=order.pk)
        else:
            messages.error(request, 'لطفاً خطاهای فرم را برطرف کنید.')
    else:
        formset = OrderItemFormSet(instance=order)
    
    return render(request, 'workflow/order_edit_prices.html', {
        'order': order,
        'formset': formset,
    })

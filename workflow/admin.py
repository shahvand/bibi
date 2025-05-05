from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Product, Driver, Order, OrderItem
import jdatetime
from django_jalali.admin.filters import JDateFieldListFilter
import django_jalali.admin as jadmin

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'branch_name')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role', 'branch_name')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'branch_name', 'is_staff')
    list_filter = UserAdmin.list_filter + ('role',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'requester', 'status', 'order_date', 'get_approval_date_jalali', 'get_delivery_date_jalali', 'get_receipt_date_jalali')
    list_filter = ('status', ('order_date', JDateFieldListFilter), ('approval_date', JDateFieldListFilter), 
                   ('delivery_date', JDateFieldListFilter), ('receipt_date', JDateFieldListFilter))
    search_fields = ('requester__username', 'requester__email', 'notes')
    inlines = [OrderItemInline]
    date_hierarchy = 'order_date'
    
    @admin.display(description='تاریخ تایید')
    def get_approval_date_jalali(self, obj):
        if obj.approval_date:
            return jdatetime.datetime.fromgregorian(datetime=obj.approval_date).strftime('%Y/%m/%d %H:%M')
        return '-'
        
    @admin.display(description='تاریخ تحویل')
    def get_delivery_date_jalali(self, obj):
        if obj.delivery_date:
            return jdatetime.datetime.fromgregorian(datetime=obj.delivery_date).strftime('%Y/%m/%d %H:%M')
        return '-'
        
    @admin.display(description='تاریخ دریافت')
    def get_receipt_date_jalali(self, obj):
        if obj.receipt_date:
            return jdatetime.datetime.fromgregorian(datetime=obj.receipt_date).strftime('%Y/%m/%d %H:%M')
        return '-'

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'unit', 'price_per_unit')
    search_fields = ('title', 'code')
    list_filter = ('unit',)

class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'phone')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(Order, OrderAdmin)

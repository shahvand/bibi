from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Product, Driver, Order, OrderItem

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
    list_display = ('id', 'requester', 'status', 'order_date', 'approval_date', 'delivery_date', 'receipt_date')
    list_filter = ('status', 'order_date', 'approval_date', 'delivery_date', 'receipt_date')
    search_fields = ('requester__username', 'requester__email', 'notes')
    inlines = [OrderItemInline]
    date_hierarchy = 'order_date'

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

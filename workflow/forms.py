from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Product, Order, OrderItem, Driver, Unit
from .templatetags.workflow_filters import format_price_input

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'role', 'branch_name']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'code', 'description', 'price_per_unit', 'current_stock', 'min_stock', 'unit_ref']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'price_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'min_stock': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'unit_ref': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # قالب‌بندی قیمت بدون نقطه اعشار و صفرهای اضافی در حالت ویرایش
        if self.instance and self.instance.pk:
            self.initial['price_per_unit'] = format_price_input(self.instance.price_per_unit)

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['name', 'phone', 'license_plate', 'is_active', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class OrderItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control product-select'})
    )
    
    class Meta:
        model = OrderItem
        fields = ['product', 'requested_quantity']
        widgets = {
            'requested_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # قالب‌بندی مقادیر بدون نقطه اعشار و صفرهای اضافی در حالت ویرایش
        if self.instance and self.instance.pk:
            self.initial['requested_quantity'] = format_price_input(self.instance.requested_quantity)

class OrderItemFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = OrderItem.objects.none()

class WarehouseOrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'requested_quantity', 'approved_quantity', 'price_per_unit', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control', 'disabled': True}),
            'requested_quantity': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True, 'step': 'any'}),
            'approved_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'price_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # قالب‌بندی مقادیر بدون نقطه اعشار و صفرهای اضافی در حالت ویرایش
        if self.instance and self.instance.pk:
            self.initial['requested_quantity'] = format_price_input(self.instance.requested_quantity)
            if self.instance.approved_quantity:
                self.initial['approved_quantity'] = format_price_input(self.instance.approved_quantity)
            if self.instance.price_per_unit:
                self.initial['price_per_unit'] = format_price_input(self.instance.price_per_unit)

class WarehouseOrderForm(forms.ModelForm):
    driver = forms.ModelChoiceField(
        queryset=Driver.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    
    class Meta:
        model = Order
        fields = ['driver', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class OrderReceiptForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add any comments about the received items...'}),
        }

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['name', 'symbol']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'symbol': forms.TextInput(attrs={'class': 'form-control'}),
        }

class RequesterOrderEditForm(forms.ModelForm):
    """فرم ویرایش سفارش توسط درخواست کننده قبل از تایید دریافت"""
    
    class Meta:
        model = Order
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'توضیحات یا دلایل تغییرات را وارد کنید...'}),
        }

class OrderItemEditForm(forms.ModelForm):
    is_rejected = forms.BooleanField(required=False, label="رد این آیتم", 
                                   widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    class Meta:
        model = OrderItem
        fields = ['product', 'requested_quantity', 'approved_quantity', 'notes', 'is_rejected']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control product-select'}),
            'requested_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '1'}),
            'approved_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control notes-field', 'rows': '1', 'style': 'height: auto; min-height: 38px;', 'placeholder': 'توضیحات تکمیلی...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # بررسی وضعیت سفارش و تنظیم فرم بر اساس آن
        is_pending = False
        if self.instance and self.instance.pk and self.instance.order:
            is_pending = self.instance.order.status == 'PENDING'
        
        # در حالت PENDING، مقدار درخواستی را نمایش می‌دهیم، در غیر این صورت مقدار تایید شده را
        if is_pending:
            self.fields['approved_quantity'].widget = forms.HiddenInput()
            self.fields['is_rejected'].widget = forms.HiddenInput()
            
            # تغییر برچسب‌ها برای حالت PENDING
            self.fields['requested_quantity'].label = 'مقدار'
            self.fields['notes'].widget.attrs['placeholder'] = 'توضیحات تکمیلی...'
            
            # محصول فقط برای آیتم‌های جدید (بدون id) قابل انتخاب است
            if self.instance.pk:
                self.fields['product'].widget.attrs['readonly'] = True
                self.fields['product'].disabled = True
        else:
            # برای سفارش‌های تایید شده
            self.fields['requested_quantity'].widget = forms.HiddenInput()
            self.fields['product'].widget = forms.HiddenInput()
            
            # تغییر برچسب‌ها برای حالت APPROVED
            self.fields['approved_quantity'].label = 'مقدار تایید شده'
            self.fields['notes'].widget.attrs['placeholder'] = 'دلیل رد یا تغییر تعداد را بنویسید'
            
            # قالب‌بندی مقادیر بدون نقطه اعشار و صفرهای اضافی در حالت ویرایش
            if self.instance and self.instance.pk:
                if self.instance.approved_quantity:
                    self.initial['approved_quantity'] = format_price_input(self.instance.approved_quantity)
                # اگر تعداد تایید شده صفر باشد، آیتم را به عنوان رد شده علامت می‌زنیم
                if self.instance.approved_quantity == 0:
                    self.initial['is_rejected'] = True
    
    def save(self, commit=True):
        """ذخیره تغییرات با در نظر گرفتن رد کردن آیتم و وضعیت سفارش"""
        item = super().save(commit=False)
        
        # در حالت PENDING، مقدار تایید شده را برابر با مقدار درخواستی قرار می‌دهیم
        if item.order.status == 'PENDING':
            item.approved_quantity = item.requested_quantity
        else:
            # در حالت APPROVED، اگر آیتم رد شده باشد، تعداد تایید شده را صفر می‌کنیم
            if self.cleaned_data.get('is_rejected', False):
                item.approved_quantity = 0
        
        if commit:
            item.save()
        
        return item 
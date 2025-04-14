from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Product, Order, OrderItem, Driver

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'role', 'branch_name']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'code', 'unit', 'price_per_unit']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'price_per_unit': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['name', 'phone', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
            'requested_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

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
            'requested_quantity': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            'approved_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_per_unit': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

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
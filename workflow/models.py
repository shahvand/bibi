from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        
        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = (
        ('REQUESTER', 'Requester'),
        ('WAREHOUSE', 'Warehouse Manager'),
        ('ACCOUNTANT', 'Accountant'),
        ('ADMIN', 'Administrator'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='REQUESTER')
    branch_name = models.CharField(max_length=100, blank=True, null=True)
    
    objects = UserManager()
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Product(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان محصول")
    code = models.CharField(max_length=20, unique=True, verbose_name="کد")
    unit = models.CharField(max_length=20, verbose_name="واحد")  # e.g., kg, piece, box
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت واحد")
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="موجودی فعلی")
    min_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="حداقل موجودی")
    
    def __str__(self):
        return f"{self.title} ({self.code})"

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"

class Driver(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('DELIVERED', 'Delivered'),
        ('RECEIVED', 'Received'),
    )
    
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_orders')
    warehouse_manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_orders', null=True, blank=True)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    order_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    receipt_date = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.requester.username} - {self.get_status_display()}"
    
    def approve(self, warehouse_manager):
        self.status = 'APPROVED'
        self.warehouse_manager = warehouse_manager
        self.approval_date = timezone.now()
        self.save()
    
    def reject(self, warehouse_manager, reason=None):
        self.status = 'REJECTED'
        self.warehouse_manager = warehouse_manager
        self.approval_date = timezone.now()
        if reason:
            self.notes = reason
        self.save()
    
    def mark_delivered(self, driver=None):
        self.status = 'DELIVERED'
        if driver:
            self.driver = driver
        self.delivery_date = timezone.now()
        self.delivered_at = timezone.now()
        self.save()
    
    def mark_received(self):
        self.status = 'RECEIVED'
        self.receipt_date = timezone.now()
        self.save()
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    requested_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    approved_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.product.title} - {self.requested_quantity} {self.product.unit}"
    
    @property
    def total_price(self):
        if self.approved_quantity and self.price_per_unit:
            return self.approved_quantity * self.price_per_unit
        return 0

    def save(self, *args, **kwargs):
        if not self.approved_quantity and self.order.status == 'PENDING':
            self.approved_quantity = self.requested_quantity
        
        if not self.price_per_unit:
            self.price_per_unit = self.product.price_per_unit
        
        super().save(*args, **kwargs)

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
import decimal

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
        ('REQUESTER', 'شعبه'),
        ('WAREHOUSE', 'انباردار'),
        ('ACCOUNTANT', 'حسابدار'),
        ('ADMIN', 'Administrator'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='REQUESTER')
    branch_name = models.CharField(max_length=100, blank=True, null=True)
    
    objects = UserManager()
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
        
    def save(self, *args, **kwargs):
        # ذخیره کاربر
        super().save(*args, **kwargs)
        
        # اگر کاربر حسابدار است، به او دسترسی‌های لازم را اضافه کن
        if self.role == 'ACCOUNTANT' and not self.is_superuser:
            from django.contrib.auth.models import Permission
            from django.contrib.contenttypes.models import ContentType
            
            # دسترسی به مدل Product
            product_content_type = ContentType.objects.get_for_model(Product)
            product_permissions = Permission.objects.filter(content_type=product_content_type)
            
            # اضافه کردن همه دسترسی‌های محصول به حسابدار
            for perm in product_permissions:
                self.user_permissions.add(perm)
                
            # دسترسی به مدل Unit
            unit_content_type = ContentType.objects.get_for_model(Unit)
            unit_permissions = Permission.objects.filter(content_type=unit_content_type)
            
            # اضافه کردن همه دسترسی‌های واحد به حسابدار
            for perm in unit_permissions:
                self.user_permissions.add(perm)

class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="نام واحد")
    symbol = models.CharField(max_length=10, verbose_name="نماد")
    
    class Meta:
        verbose_name = "واحد"
        verbose_name_plural = "واحدها"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.symbol})"

class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان")
    code = models.CharField(max_length=100, unique=True, verbose_name="کد")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    price_per_unit = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="قیمت واحد")
    unit_id = models.CharField(max_length=20, default="pc", verbose_name="شناسه واحد") 
    unit = models.CharField(max_length=20, verbose_name="واحد (قدیمی)")
    unit_ref = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="واحد")
    
    class Meta:
        verbose_name = "کالا"
        verbose_name_plural = "کالاها"
        ordering = ['title']
    
    def __str__(self):
        if self.unit_ref:
            return f"{self.title} ({self.code})"
        else:
            return f"{self.title} ({self.code})"

class Driver(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام راننده")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="شماره تماس")
    license_plate = models.CharField(max_length=20, blank=True, null=True, verbose_name="شماره پلاک")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    notes = models.TextField(blank=True, null=True, verbose_name="یادداشت‌ها")
    
    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'در انتظار تایید'),
        ('APPROVED', 'تایید شده'),
        ('READY', 'آماده ارسال'),
        ('SHIPPING', 'در حال ارسال'),
        ('DELIVERED', 'تحویل راننده شده'),
        ('REJECTED', 'رد شده'),
        ('CANCELLED', 'لغو شده'),
        ('RECEIVED', 'دریافت شده'),
    )
    
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_orders')
    warehouse_manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_orders', null=True, blank=True)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    order_date = models.DateTimeField(auto_now_add=True)
    last_edit_time = models.DateTimeField(auto_now=True, verbose_name="زمان آخرین ویرایش")
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
    
    requested_quantity = models.DecimalField(max_digits=15, decimal_places=0)
    approved_quantity = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True)
    price_per_unit = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True)
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
        
        # Validate that approved_quantity doesn't exceed database limits
        if self.approved_quantity:
            max_allowed = decimal.Decimal('999999999999999')  # 15 digits (max_digits=15)
            if self.approved_quantity > max_allowed:
                self.approved_quantity = max_allowed
        
        super().save(*args, **kwargs)

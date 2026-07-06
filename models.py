from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=10, default='🍽')
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    VEG = 'veg'
    NON_VEG = 'nonveg'
    FOOD_TYPE_CHOICES = [(VEG, 'Veg'), (NON_VEG, 'Non-Veg')]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    emoji = models.CharField(max_length=10, default='🍽')
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    food_type = models.CharField(max_length=10, choices=FOOD_TYPE_CHOICES, default=VEG)
    is_bestseller = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    spice_level = models.PositiveSmallIntegerField(default=0)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class Table(models.Model):
    AVAILABLE = 'available'
    OCCUPIED = 'occupied'
    BILLING = 'billing'
    STATUS_CHOICES = [(AVAILABLE, 'Available'), (OCCUPIED, 'Occupied'), (BILLING, 'Billing')]

    number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField(default=4)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=AVAILABLE)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f'Table {self.number}'

    def generate_qr(self):
        import qrcode
        from io import BytesIO
        from django.core.files import File
        url = f'http://localhost:8000/menu/?table={self.number}'
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        buf = BytesIO()
        img.save(buf, format='PNG')
        self.qr_code.save(f'table_{self.number}_qr.png', File(buf), save=False)


class Order(models.Model):
    PENDING = 'pending'
    PREPARING = 'preparing'
    READY = 'ready'
    SERVED = 'served'
    PAID = 'paid'
    STATUS_CHOICES = [
        (PENDING,'Pending'),(PREPARING,'Preparing'),
        (READY,'Ready'),(SERVED,'Served'),(PAID,'Paid'),
    ]

    order_id = models.CharField(max_length=20, unique=True, blank=True)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    payment_status = models.CharField(max_length=20, default='pending')
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order {self.order_id}'

    def save(self, *args, **kwargs):
        if not self.order_id:
            import random
            self.order_id = f'SG{timezone.now().strftime("%d%m")}{random.randint(100,999)}'
        super().save(*args, **kwargs)

    def calculate_totals(self):
        self.subtotal = sum(item.line_total for item in self.items.all())
        self.gst_amount = round(float(self.subtotal) * 0.05, 2)
        self.total_amount = float(self.subtotal) + float(self.gst_amount) - float(self.discount)
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True)
    item_name = models.CharField(max_length=200)
    item_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    special_note = models.CharField(max_length=300, blank=True)

    @property
    def line_total(self):
        return float(self.item_price) * self.quantity

    def __str__(self):
        return f'{self.quantity}x {self.item_name}'

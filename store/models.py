from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.name

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('online', 'Online Payment'),
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
        ('wallet', 'Digital Wallet'),
    ]
    
    SHIPPING_METHOD_CHOICES = [
        ('standard', 'Standard Delivery (3-5 days)'),
        ('express', 'Express Delivery (1-2 days)'),
        ('same_day', 'Same Day Delivery'),
    ]
    
    # Customer Info
    user = models.ForeignKey('auth.User', related_name='orders', on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    
    # Address
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Nepal')
    
    # Order Details
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    
    # Shipping
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_METHOD_CHOICES, default='standard')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tracking_number = models.CharField(max_length=100, blank=True)
    shipping_carrier = models.CharField(max_length=50, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    
    # Cancellation & Returns
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    return_reason = models.TextField(blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    # Financial
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Notes
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created']

    def get_total(self):
        total = sum(item.get_cost() for item in self.items.all())
        return total
    
    def calculate_total(self):
        self.subtotal = self.get_total()
        self.total = self.subtotal + self.shipping_cost - self.discount_amount + self.tax_amount
        return self.total
    
    def __str__(self):
        return f'Order #{self.id} - {self.get_status_display()}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def get_cost(self):
        return self.price * self.quantity
    
    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    title = models.CharField(max_length=100)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    verified_purchase = models.BooleanField(default=False)
    helpful_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created']
        unique_together = ['product', 'user']

    def __str__(self):
        return f'{self.user.username} - {self.product.name} - {self.rating} stars'

class Wishlist(models.Model):
    user = models.ForeignKey('auth.User', related_name='wishlist', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='wishlist_items', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        unique_together = ['user', 'product']

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'

class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.email

class SocialShare(models.Model):
    product = models.ForeignKey(Product, related_name='social_shares', on_delete=models.CASCADE)
    platform = models.CharField(max_length=20, choices=[
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email')
    ])
    share_count = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        unique_together = ['product', 'platform']

    def __str__(self):
        return f'{self.product.name} - {self.platform}'

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.name} - {self.subject[:30]}'


# =====================================================
# PHASE 1: ORDER TRACKING & MANAGEMENT
# =====================================================

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, related_name='status_history', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Order.ORDER_STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f'Order #{self.order.id} - {self.get_status_display()} at {self.changed_at}'


# =====================================================
# PHASE 2: USER ADDRESS BOOK
# =====================================================

class UserAddress(models.Model):
    ADDRESS_TYPE_CHOICES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey('auth.User', related_name='addresses', on_delete=models.CASCADE)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='home')
    name = models.CharField(max_length=100)  # Label like "My Home"
    recipient_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Nepal')
    is_default = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_default', '-created']

    def __str__(self):
        return f'{self.name} - {self.recipient_name}'


# =====================================================
# PHASE 2: RECENTLY VIEWED PRODUCTS
# =====================================================

class RecentlyViewed(models.Model):
    user = models.ForeignKey('auth.User', related_name='recently_viewed', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='recent_views', on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-viewed_at']
        unique_together = ['user', 'product']

    def __str__(self):
        return f'{self.user.username} viewed {self.product.name}'


# =====================================================
# PHASE 3: COUPON & DISCOUNT SYSTEM
# =====================================================

class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)  # % or amount
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Validity
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Usage limits
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    per_user_limit = models.PositiveIntegerField(default=1)
    
    # Applicability
    applicable_products = models.ManyToManyField(Product, blank=True, related_name='coupons')
    applicable_categories = models.ManyToManyField(Category, blank=True, related_name='coupons')
    exclude_sale_items = models.BooleanField(default=True)
    
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.code} - {self.name}'
    
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.start_date or now > self.end_date:
            return False
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        return True


class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, related_name='usages', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', related_name='coupon_usages', on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name='coupon_usage', on_delete=models.CASCADE)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['coupon', 'order']

    def __str__(self):
        return f'{self.coupon.code} used by {self.user.username}'


# =====================================================
# PHASE 4: STOCK ALERTS & NOTIFICATIONS
# =====================================================

class StockAlert(models.Model):
    product = models.ForeignKey(Product, related_name='stock_alerts', on_delete=models.CASCADE)
    threshold = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    alert_sent = models.BooleanField(default=False)
    last_alert_sent = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'Stock Alert for {self.product.name} (Threshold: {self.threshold})'


class BackInStockNotification(models.Model):
    user = models.ForeignKey('auth.User', related_name='back_in_stock_notifications', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='back_in_stock_subscribers', on_delete=models.CASCADE)
    email = models.EmailField()
    is_notified = models.BooleanField(default=False)
    notified_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-created']

    def __str__(self):
        return f'{self.user.username} waiting for {self.product.name}'


# =====================================================
# PHASE 6: ABANDONED CART
# =====================================================

class AbandonedCart(models.Model):
    user = models.ForeignKey('auth.User', related_name='abandoned_carts', on_delete=models.CASCADE)
    cart_data = models.JSONField()  # Store cart items as JSON
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    reminder_sent = models.BooleanField(default=False)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    converted = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-updated']

    def __str__(self):
        return f'Abandoned Cart - {self.user.username} - ${self.total}'

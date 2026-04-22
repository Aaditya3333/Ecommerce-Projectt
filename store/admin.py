from django.contrib import admin
from .models import (
    Category, Product, Review, Order, OrderItem, Wishlist, Newsletter, 
    ContactMessage, OrderStatusHistory, UserAddress, RecentlyViewed,
    Coupon, CouponUsage, StockAlert, BackInStockNotification, AbandonedCart
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    ordering = ['name']
    list_per_page = 20

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'available', 'created']
    list_filter = ['category', 'available', 'created']
    search_fields = ['name', 'description', 'category__name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['available']
    ordering = ['-created']
    list_per_page = 20
    readonly_fields = ['created', 'updated']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock', 'available')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Metadata', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'verified_purchase', 'created', 'helpful_count']
    list_filter = ['rating', 'verified_purchase', 'created']
    search_fields = ['product__name', 'user__username', 'title', 'content']
    readonly_fields = ['created', 'updated']
    list_editable = ['verified_purchase']
    ordering = ['-created']
    list_per_page = 20

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'created', 'paid', 'payment_method']
    list_filter = ['paid', 'payment_method', 'created']
    search_fields = ['first_name', 'last_name', 'email']
    ordering = ['-created']
    list_per_page = 20
    readonly_fields = ['created', 'updated']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    list_filter = ['order__created', 'product__category']
    search_fields = ['product__name', 'order__email']
    ordering = ['-order__created']
    list_per_page = 20

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created']
    list_filter = ['created']
    search_fields = ['user__username', 'product__name']
    ordering = ['-created']
    list_per_page = 20

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'created']
    list_filter = ['is_active', 'created']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created']
    list_per_page = 20
    list_editable = ['is_active']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created', 'is_read']
    list_filter = ['is_read', 'created']
    search_fields = ['name', 'email', 'subject', 'message']
    ordering = ['-created']
    list_per_page = 20
    list_editable = ['is_read']
    readonly_fields = ['created']

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'changed_at', 'changed_by']
    list_filter = ['status', 'changed_at']
    search_fields = ['order__id', 'notes']
    ordering = ['-changed_at']
    list_per_page = 20

@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'recipient_name', 'city', 'is_default', 'created']
    list_filter = ['is_default', 'city', 'country']
    search_fields = ['user__username', 'name', 'recipient_name', 'address']
    ordering = ['-is_default', '-created']
    list_per_page = 20

@admin.register(RecentlyViewed)
class RecentlyViewedAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['user__username', 'product__name']
    ordering = ['-viewed_at']
    list_per_page = 20

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'discount_type', 'discount_value', 'is_active', 'usage_count', 'created']
    list_filter = ['discount_type', 'is_active', 'created']
    search_fields = ['code', 'name', 'description']
    ordering = ['-created']
    list_per_page = 20
    filter_horizontal = ['applicable_products', 'applicable_categories']

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'user', 'order', 'discount_amount', 'used_at']
    list_filter = ['used_at']
    search_fields = ['coupon__code', 'user__username']
    ordering = ['-used_at']
    list_per_page = 20

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['product', 'threshold', 'alert_sent', 'last_alert_sent', 'is_active']
    list_filter = ['is_active', 'alert_sent', 'created']
    search_fields = ['product__name']
    ordering = ['-created']
    list_per_page = 20

@admin.register(BackInStockNotification)
class BackInStockNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'email', 'is_notified', 'created']
    list_filter = ['is_notified', 'created']
    search_fields = ['user__username', 'product__name', 'email']
    ordering = ['-created']
    list_per_page = 20

@admin.register(AbandonedCart)
class AbandonedCartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total', 'reminder_sent', 'converted', 'updated']
    list_filter = ['reminder_sent', 'converted', 'created']
    search_fields = ['user__username']
    ordering = ['-updated']
    list_per_page = 20

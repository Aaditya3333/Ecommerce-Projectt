from django.contrib import admin
from .models import Category, Product, Review, Order, OrderItem, Wishlist, Newsletter

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

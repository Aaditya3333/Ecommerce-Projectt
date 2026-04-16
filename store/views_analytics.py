from django.shortcuts import render
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Product, Order, OrderItem, Category, Review
from django.contrib.auth.decorators import login_required

@login_required
def sales_dashboard(request):
    # Only allow admin users
    if not request.user.is_staff:
        return render(request, 'store/analytics/access_denied.html')
    
    # Get date ranges
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    
    # Sales Statistics
    total_orders = Order.objects.count()
    total_revenue = OrderItem.objects.aggregate(
        total=Sum('price')
    )['total'] or 0
    
    # Last 30 days stats
    orders_last_30 = Order.objects.filter(created__gte=last_30_days).count()
    revenue_last_30 = OrderItem.objects.filter(
        order__created__gte=last_30_days
    ).aggregate(total=Sum('price'))['total'] or 0
    
    # Last 7 days stats
    orders_last_7 = Order.objects.filter(created__gte=last_7_days).count()
    revenue_last_7 = OrderItem.objects.filter(
        order__created__gte=last_7_days
    ).aggregate(total=Sum('price'))['total'] or 0
    
    # Top Products
    top_products = OrderItem.objects.values(
        'product__name', 'product__id'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('price')
    ).order_by('-total_sold')[:10]
    
    # Top Categories
    top_categories = OrderItem.objects.values(
        'product__category__name'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('price')
    ).order_by('-total_sold')[:10]
    
    # Recent Orders
    recent_orders = Order.objects.order_by('-created')[:10]
    
    # Product Statistics
    total_products = Product.objects.count()
    available_products = Product.objects.filter(available=True).count()
    out_of_stock = Product.objects.filter(available=False).count()
    
    # Customer Statistics
    total_customers = Order.objects.values('email').distinct().count()
    
    # Review Statistics
    total_reviews = Review.objects.count()
    avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0
    
    # Daily Sales Data (Last 7 days)
    daily_sales = []
    for i in range(7):
        date = today - timedelta(days=i)
        sales = OrderItem.objects.filter(
            order__created__date=date
        ).aggregate(total=Sum('price'))['total'] or 0
        daily_sales.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': sales
        })
    
    daily_sales.reverse()  # Show oldest to newest
    
    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'orders_last_30': orders_last_30,
        'revenue_last_30': revenue_last_30,
        'orders_last_7': orders_last_7,
        'revenue_last_7': revenue_last_7,
        'top_products': top_products,
        'top_categories': top_categories,
        'recent_orders': recent_orders,
        'total_products': total_products,
        'available_products': available_products,
        'out_of_stock': out_of_stock,
        'total_customers': total_customers,
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
        'daily_sales': daily_sales,
    }
    
    return render(request, 'store/analytics/sales_dashboard.html', context)

@login_required
def product_analytics(request):
    if not request.user.is_staff:
        return render(request, 'store/analytics/access_denied.html')
    
    # Product performance data
    products = Product.objects.annotate(
        total_sold=Sum('order_items__quantity'),
        total_revenue=Sum('order_items__price'),
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-total_sold')
    
    context = {
        'products': products,
    }
    
    return render(request, 'store/analytics/product_analytics.html', context)

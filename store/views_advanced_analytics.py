from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg, Q, F, DecimalField
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from .models import Product, Category, Order, OrderItem, Review, Wishlist
import json

@login_required
def advanced_analytics_dashboard(request):
    """Advanced analytics dashboard with real-time data"""
    
    # Check if user is admin/staff
    if not request.user.is_staff:
        return render(request, 'store/analytics/access_denied.html')
    
    # Get date ranges
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    
    # Sales Analytics
    sales_data = get_sales_analytics(last_30_days, today)
    
    # Product Analytics
    product_data = get_product_analytics()
    
    # Customer Analytics
    customer_data = get_customer_analytics(last_30_days, today)
    
    # Category Analytics
    category_data = get_category_analytics()
    
    # Real-time metrics
    real_time_data = get_real_time_metrics()
    
    context = {
        'sales_data': sales_data,
        'product_data': product_data,
        'customer_data': customer_data,
        'category_data': category_data,
        'real_time_data': real_time_data,
        'date_range': {
            'start': last_30_days,
            'end': today
        }
    }
    
    return render(request, 'store/analytics/advanced_dashboard.html', context)

def get_sales_analytics(start_date, end_date):
    """Comprehensive sales analytics"""
    
    # Daily sales trend
    daily_sales = Order.objects.filter(
        created__date__range=[start_date, end_date]
    ).annotate(
        day=TruncDay('created')
    ).values('day').annotate(
        total_sales=Sum(F('items__price') * F('items__quantity'), output_field=DecimalField()),
        order_count=Count('id')
    ).order_by('day')
    
    # Weekly comparison
    weekly_comparison = Order.objects.filter(
        created__date__range=[start_date, end_date]
    ).annotate(
        week=TruncWeek('created')
    ).values('week').annotate(
        total_sales=Sum(F('items__price') * F('items__quantity'), output_field=DecimalField()),
        order_count=Count('id')
    ).order_by('week')
    
    # Monthly revenue
    monthly_revenue = Order.objects.filter(
        created__date__range=[start_date, end_date]
    ).annotate(
        month=TruncMonth('created')
    ).values('month').annotate(
        revenue=Sum(F('items__price') * F('items__quantity'), output_field=DecimalField()),
        orders=Count('id')
    ).order_by('month')
    
    # Top selling products
    top_products = OrderItem.objects.filter(
        order__created__date__range=[start_date, end_date]
    ).values('product__name').annotate(
        total_sold=Sum('quantity'),
        revenue=Sum(F('price') * F('quantity'), output_field=DecimalField())
    ).order_by('-total_sold')[:10]
    
    # Payment method breakdown
    payment_methods = Order.objects.filter(
        created__date__range=[start_date, end_date]
    ).values('payment_method').annotate(
        count=Count('id'),
        total=Sum(F('items__price') * F('items__quantity'), output_field=DecimalField())
    ).order_by('-count')
    
    return {
        'daily_sales': list(daily_sales),
        'weekly_comparison': list(weekly_comparison),
        'monthly_revenue': list(monthly_revenue),
        'top_products': list(top_products),
        'payment_methods': list(payment_methods),
        'total_revenue': Order.objects.filter(
            created__date__range=[start_date, end_date]
        ).aggregate(total=Sum(F('items__price') * F('items__quantity'), output_field=DecimalField()))['total'] or 0,
        'total_orders': Order.objects.filter(
            created__date__range=[start_date, end_date]
        ).count(),
        'average_order_value': Order.objects.filter(
            created__date__range=[start_date, end_date]
        ).aggregate(avg=Avg(F('items__price') * F('items__quantity'), output_field=DecimalField()))['avg'] or 0
    }

def get_product_analytics():
    """Detailed product analytics"""
    
    # Product performance metrics
    products = Product.objects.annotate(
        total_orders=Count('order_items'),
        total_revenue=Sum(F('order_items__price') * F('order_items__quantity'), output_field=DecimalField()),
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews'),
        wishlist_count=Count('wishlist_items')
    ).order_by('-total_revenue')
    
    # Low stock alerts
    low_stock_products = Product.objects.filter(
        available=True,
        stock__lt=10  # Alert when less than 10 items
    ).order_by('stock')
    
    # Most viewed products (placeholder - would need view tracking implementation)
    most_viewed = Product.objects.annotate(
        view_count=Count('order_items', distinct=True)
    ).order_by('-view_count')[:10]
    
    # Conversion rates by category
    category_conversion = Category.objects.annotate(
        product_count=Count('products'),
        total_orders=Count('products__order_items'),
        conversion_rate=Count('products__order_items') * 100.0 / Count('products', distinct=True)
    ).order_by('-conversion_rate')
    
    return {
        'top_performing': list(products[:10]),
        'low_stock': list(low_stock_products),
        'most_viewed': list(most_viewed),
        'category_conversion': list(category_conversion),
        'total_products': Product.objects.count(),
        'available_products': Product.objects.filter(available=True).count(),
        'out_of_stock': Product.objects.filter(available=False).count()
    }

def get_customer_analytics(start_date, end_date):
    """Customer behavior analytics"""
    
    # New vs returning customers
    total_orders = Order.objects.filter(created__date__range=[start_date, end_date])
    unique_customers = total_orders.values('email').distinct().count()
    
    # Customer lifetime value
    customer_ltv = Order.objects.values('email').annotate(
        total_spent=Sum(F('items__price') * F('items__quantity'), output_field=DecimalField()),
        order_count=Count('id')
    ).order_by('-total_spent')
    
    # Customer segmentation
    customer_segments = {
        'vip': customer_ltv.filter(total_spent__gte=1000).count(),
        'regular': customer_ltv.filter(total_spent__gte=100, total_spent__lt=1000).count(),
        'new': customer_ltv.filter(total_spent__lt=100).count()
    }
    
    # Retention rate
    retention_data = calculate_retention_rate(start_date, end_date)
    
    return {
        'total_customers': unique_customers,
        'customer_segments': customer_segments,
        'top_customers': list(customer_ltv[:10]),
        'retention_rate': retention_data,
        'average_customer_value': customer_ltv.aggregate(avg=Avg('total_spent'))['avg'] or 0
    }

def get_category_analytics():
    """Category performance analytics"""
    
    categories = Category.objects.annotate(
        product_count=Count('products'),
        total_revenue=Sum(F('products__order_items__price') * F('products__order_items__quantity'), output_field=DecimalField()),
        total_orders=Count('products__order_items'),
        average_rating=Avg('products__reviews__rating')
    ).order_by('-total_revenue')
    
    return {
        'category_performance': list(categories),
        'total_categories': Category.objects.count(),
        'top_revenue_category': categories.first(),
        'most_products_category': categories.order_by('-product_count').first()
    }

def get_real_time_metrics():
    """Real-time dashboard metrics"""
    
    today = timezone.now().date()
    
    return {
        'today_sales': Order.objects.filter(created__date=today).count(),
        'today_revenue': Order.objects.filter(created__date=today).aggregate(
            total=Sum(F('items__price') * F('items__quantity'), output_field=DecimalField())
        )['total'] or 0,
        'active_users': 0,  # Would need session tracking
        'online_visitors': 0,  # Would need real-time tracking
        'conversion_rate': calculate_conversion_rate(),
        'cart_abandonment_rate': calculate_cart_abandonment_rate(),
        'average_session_duration': 0,  # Would need session tracking
        'bounce_rate': 0  # Would need session tracking
    }

def calculate_retention_rate(start_date, end_date):
    """Calculate customer retention rate"""
    
    # Get customers from previous period
    previous_start = start_date - timedelta(days=30)
    previous_end = start_date
    
    previous_customers = set(Order.objects.filter(
        created__date__range=[previous_start, previous_end]
    ).values_list('email', flat=True))
    
    # Get customers from current period
    current_customers = set(Order.objects.filter(
        created__date__range=[start_date, end_date]
    ).values_list('email', flat=True))
    
    # Calculate retention rate
    if previous_customers:
        retained_customers = previous_customers.intersection(current_customers)
        retention_rate = (len(retained_customers) / len(previous_customers)) * 100
    else:
        retention_rate = 0
    
    return {
        'rate': retention_rate,
        'previous_customers': len(previous_customers),
        'current_customers': len(current_customers),
        'retained_customers': len(previous_customers.intersection(current_customers))
    }

def calculate_conversion_rate():
    """Calculate overall conversion rate"""
    
    # This would need session/cart tracking
    # For now, return a placeholder
    return 3.5

def calculate_cart_abandonment_rate():
    """Calculate cart abandonment rate"""
    
    # This would need cart tracking
    # For now, return a placeholder
    return 68.5

@login_required
def analytics_api_data(request):
    """API endpoint for analytics data"""
    
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'})
    
    data_type = request.GET.get('type', 'sales')
    period = request.GET.get('period', '30d')
    
    # Calculate date range
    if period == '7d':
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=7)
    elif period == '90d':
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=90)
    else:  # 30d default
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    
    if data_type == 'sales':
        data = get_sales_analytics(start_date, end_date)
    elif data_type == 'products':
        data = get_product_analytics()
    elif data_type == 'customers':
        data = get_customer_analytics(start_date, end_date)
    elif data_type == 'categories':
        data = get_category_analytics()
    else:
        data = get_real_time_metrics()
    
    return JsonResponse({'data': data})

@login_required
def export_analytics(request):
    """Export analytics data to CSV/Excel"""
    
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'})
    
    export_type = request.GET.get('type', 'sales')
    
    # Implementation for exporting data
    # This would generate and return CSV/Excel files
    return JsonResponse({'message': f'Export {export_type} functionality not yet implemented'})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Category, Product, Order, OrderItem, Review, ContactMessage, Newsletter
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
import csv
import io

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    # Basic counts
    categories = Category.objects.all()
    products = Product.objects.all()
    in_stock_products = products.filter(available=True)
    out_of_stock_products = products.filter(available=False)
    
    # Order statistics
    orders = Order.objects.all()
    total_orders = orders.count()
    paid_orders = orders.filter(paid=True)
    total_revenue = paid_orders.aggregate(total=Sum('total'))['total'] or 0
    pending_orders = orders.filter(paid=False).count()
    
    # Recent orders (last 7 days)
    last_week = timezone.now() - timedelta(days=7)
    recent_orders = orders.filter(created__gte=last_week)
    recent_revenue = recent_orders.filter(paid=True).aggregate(total=Sum('total'))['total'] or 0
    
    # Top products by sales
    top_products = Product.objects.annotate(
        sold_count=Sum('orderitem__quantity', filter=Q(orderitem__order__paid=True))
    ).order_by('-sold_count')[:5]
    
    # Low stock products
    low_stock = products.filter(stock__lte=5, available=True)[:5]
    
    # User statistics
    total_users = User.objects.filter(is_superuser=False).count()
    new_users_last_week = User.objects.filter(date_joined__gte=last_week, is_superuser=False).count()
    
    # Review statistics
    total_reviews = Review.objects.count()
    avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0
    
    # Contact messages
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    
    # Newsletter subscribers
    newsletter_count = Newsletter.objects.filter(is_active=True).count()
    
    # Sales data for chart (last 30 days)
    sales_data = []
    labels = []
    for i in range(30, 0, -1):
        date = timezone.now() - timedelta(days=i)
        day_sales = orders.filter(
            created__date=date.date(),
            paid=True
        ).aggregate(total=Sum('total'))['total'] or 0
        sales_data.append(float(day_sales))
        labels.append(date.strftime('%d %b'))
    
    context = {
        'categories': categories,
        'products': products,
        'in_stock_count': in_stock_products.count(),
        'out_of_stock_count': out_of_stock_products.count(),
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'recent_revenue': recent_revenue,
        'top_products': top_products,
        'low_stock': low_stock,
        'total_users': total_users,
        'new_users': new_users_last_week,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1),
        'unread_messages': unread_messages,
        'newsletter_count': newsletter_count,
        'sales_data': json.dumps(sales_data),
        'sales_labels': json.dumps(labels),
    }
    return render(request, 'store/admin/dashboard.html', context)

@login_required
def admin_categories(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    categories = Category.objects.all()
    return render(request, 'store/admin/categories.html', {'categories': categories})

@login_required
def admin_products(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    products = Product.objects.all()
    return render(request, 'store/admin/products.html', {'products': products})

@login_required
def admin_create_category(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        slug = name.lower().replace(' ', '-')
        
        Category.objects.create(name=name, description=description, image=image, slug=slug)
        messages.success(request, 'Category created successfully!')
        return redirect('admin_categories')
    
    return render(request, 'store/admin/create_category.html')

@login_required
def admin_create_product(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        category_id = request.POST.get('category')
        image = request.FILES.get('image')
        slug = name.lower().replace(' ', '-')
        
        category = get_object_or_404(Category, id=category_id)
        Product.objects.create(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category=category,
            image=image,
            slug=slug
        )
        messages.success(request, 'Product created successfully!')
        return redirect('admin_products')
    
    categories = Category.objects.all()
    return render(request, 'store/admin/create_product.html', {'categories': categories})

def admin_edit_category(request, category_id):
    if not request.user.is_superuser:
        return redirect('home')
    
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        
        category.name = name
        category.description = description
        if image:
            category.image = image
        
        category.save()
        messages.success(request, 'Category updated successfully!')
        return redirect('admin_categories')
    
    return render(request, 'store/admin/edit_category.html', {'category': category})

def admin_delete_category(request, category_id):
    if not request.user.is_superuser:
        return redirect('home')
    
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('admin_categories')

def admin_edit_product(request, product_id):
    if not request.user.is_superuser:
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        category_id = request.POST.get('category')
        image = request.FILES.get('image')
        slug = name.lower().replace(' ', '-')
        
        category = get_object_or_404(Category, id=category_id)
        
        product.name = name
        product.description = description
        product.price = price
        product.stock = stock
        product.category = category
        if image:
            product.image = image
        
        product.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('admin_products')
    
    return render(request, 'store/admin/edit_product.html', {'product': product, 'categories': categories})

def admin_delete_product(request, product_id):
    if not request.user.is_superuser:
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'Product deleted successfully!')
    return redirect('admin_products')

import csv
import io

@login_required
def admin_export_products(request):
    """Export products to CSV"""
    if not request.user.is_superuser:
        return redirect('home')
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['ID', 'Name', 'Category', 'Price', 'Stock', 'Available', 'Description'])
    
    # Write products
    products = Product.objects.all()
    for product in products:
        writer.writerow([
            product.id,
            product.name,
            product.category.name,
            product.price,
            product.stock,
            'Yes' if product.available else 'No',
            product.description[:100]
        ])
    
    output.seek(0)
    response = HttpResponse(output, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products_export.csv"'
    return response

@login_required
def admin_import_products(request):
    """Import products from CSV"""
    if not request.user.is_superuser:
        return redirect('home')
    
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('admin_products')
        
        try:
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            success_count = 0
            error_count = 0
            
            for row in reader:
                try:
                    category_name = row.get('Category', 'Uncategorized')
                    category, _ = Category.objects.get_or_create(name=category_name)
                    
                    Product.objects.create(
                        name=row['Name'],
                        category=category,
                        price=float(row['Price']),
                        stock=int(row['Stock']),
                        available=row.get('Available', 'Yes').lower() == 'yes',
                        description=row.get('Description', ''),
                        slug=row['Name'].lower().replace(' ', '-')
                    )
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    continue
            
            messages.success(request, f'Imported {success_count} products successfully!')
            if error_count > 0:
                messages.warning(request, f'{error_count} products could not be imported.')
                
        except Exception as e:
            messages.error(request, f'Error importing file: {str(e)}')
        
        return redirect('admin_products')
    
    return render(request, 'store/admin/import_products.html')

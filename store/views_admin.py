from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Category, Product
from django.contrib import messages

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    categories = Category.objects.all()
    products = Product.objects.all()
    in_stock_products = products.filter(available=True)
    out_of_stock_products = products.filter(available=False)
    
    context = {
        'categories': categories,
        'products': products,
        'in_stock_count': in_stock_products.count(),
        'out_of_stock_count': out_of_stock_products.count(),
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

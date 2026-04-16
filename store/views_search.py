from django.shortcuts import render
from django.db.models import Q
from .models import Product, Category
from django.core.paginator import Paginator

def search(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort', 'relevance')
    
    products = Product.objects.filter(available=True)
    
    # Apply search filters
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    # Apply sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created')
    elif sort_by == 'rating':
        # Sort by average rating (this would require more complex calculation)
        products = products.order_by('-created')  # Fallback to newest
    else:  # relevance
        if query:
            # Simple relevance: prioritize name matches over description
            products = products.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            ).extra(
                select={'relevance': 'CASE WHEN name LIKE %s THEN 2 WHEN description LIKE %s THEN 1 ELSE 0 END'},
                select_params=([f'%{query}%', f'%{query}%']),
                order_by=['-relevance', '-created']
            )
        else:
            products = products.order_by('-created')
    
    # Get categories for filter
    categories = Category.objects.all()
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'categories': categories,
        'selected_category': category_id,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'total_results': products.count(),
    }
    
    return render(request, 'store/search/search_results.html', context)

def search_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = []
    
    if len(query) >= 2:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query),
            available=True
        )[:5]
        
        for product in products:
            suggestions.append({
                'name': product.name,
                'url': f"/product/{product.pk}/",
                'image': product.image.url if product.image else None,
                'price': str(product.price)
            })
    
    return render(request, 'store/search/suggestions.html', {'suggestions': suggestions})

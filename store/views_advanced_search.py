from django.shortcuts import render
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Product, Category, Review
from .forms import AdvancedSearchForm
import json

def advanced_search(request):
    """Advanced product search with multiple filters"""
    
    form = AdvancedSearchForm(request.GET or None)
    products = Product.objects.filter(available=True)
    
    # Apply filters
    if form.is_valid():
        # Search query
        if form.cleaned_data.get('query'):
            query = form.cleaned_data['query']
            products = products.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            )
        
        # Category filter
        if form.cleaned_data.get('category'):
            products = products.filter(category=form.cleaned_data['category'])
        
        # Price range filter
        min_price = form.cleaned_data.get('min_price')
        if min_price:
            products = products.filter(price__gte=min_price)
        
        max_price = form.cleaned_data.get('max_price')
        if max_price:
            products = products.filter(price__lte=max_price)
        
        # Stock filter
        if form.cleaned_data.get('in_stock'):
            products = products.filter(stock__gt=0)
        
        # Sorting
        sort_by = form.cleaned_data.get('sort_by')
        if sort_by:
            products = products.order_by(sort_by)
    
    # Add annotations for ratings and review count
    products = products.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get search suggestions
    suggestions = []
    if request.GET.get('query'):
        suggestions = get_search_suggestions(request.GET.get('query'))
    
    context = {
        'form': form,
        'products': page_obj,
        'suggestions': suggestions,
        'total_results': products.count(),
        'page_obj': page_obj
    }
    
    return render(request, 'store/search/advanced_search.html', context)

def get_search_suggestions(query):
    """Get search suggestions based on query"""
    if not query or len(query) < 2:
        return []
    
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(category__name__icontains=query)
    ).filter(available=True)[:5]
    
    suggestions = []
    for product in products:
        suggestions.append({
            'name': product.name,
            'category': product.category.name,
            'price': str(product.price),
            'image': product.image.url if product.image else None,
            'url': f'/product/{product.id}/'
        })
    
    return suggestions

def search_suggestions_api(request):
    """API endpoint for search suggestions"""
    query = request.GET.get('q', '')
    suggestions = get_search_suggestions(query)
    
    return JsonResponse({'suggestions': suggestions})

def popular_searches(request):
    """Get popular search terms (placeholder for analytics integration)"""
    # This would typically come from search analytics
    popular_terms = [
        {'term': 'laptop', 'count': 245},
        {'term': 'smartphone', 'count': 189},
        {'term': 'headphones', 'count': 156},
        {'term': 'watch', 'count': 134},
        {'term': 'tablet', 'count': 98}
    ]
    
    return JsonResponse({'popular_searches': popular_terms})

def search_history(request):
    """Get user's search history"""
    if request.user.is_authenticated:
        # This would typically come from user's search history
        history = request.session.get('search_history', [])
        return JsonResponse({'history': history})
    else:
        return JsonResponse({'history': []})

def save_search(request):
    """Save search term to user history"""
    if request.method == 'POST':
        query = request.POST.get('query', '')
        if query and len(query) > 2:
            # Save to session for anonymous users
            if not request.user.is_authenticated:
                history = request.session.get('search_history', [])
                if query not in history:
                    history.insert(0, query)
                    history = history[:10]  # Keep last 10 searches
                    request.session['search_history'] = history
            # For authenticated users, save to database
            else:
                # This would save to a UserSearchHistory model
                pass
    
    return JsonResponse({'success': True})

def autocomplete_search(request):
    """Autocomplete search with product names and categories"""
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    # Search products
    products = Product.objects.filter(
        name__icontains=query,
        available=True
    ).values('id', 'name', 'category__name')[:5]
    
    # Search categories
    categories = Category.objects.filter(
        name__icontains=query
    ).values('id', 'name')[:3]
    
    results = []
    
    # Add product results
    for product in products:
        results.append({
            'type': 'product',
            'id': product['id'],
            'name': product['name'],
            'category': product['category__name'],
            'url': f'/product/{product["id"]}/'
        })
    
    # Add category results
    for category in categories:
        results.append({
            'type': 'category',
            'id': category['id'],
            'name': category['name'],
            'url': f'/category/{category["id"]}/'
        })
    
    return JsonResponse({'results': results})

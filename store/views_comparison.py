from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import models
from .models import Product

def add_to_comparison(request):
    product_id = request.GET.get('product_id')
    
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Please login to compare products'}, status=401)
    
    comparison_list = request.session.get('comparison_list', [])
    
    if product_id not in comparison_list:
        if len(comparison_list) >= 4:
            return JsonResponse({'error': 'You can compare maximum 4 products at a time'}, status=400)
        
        comparison_list.append(product_id)
        request.session['comparison_list'] = comparison_list
    
    return JsonResponse({'success': True, 'count': len(comparison_list)})

def remove_from_comparison(request):
    product_id = request.GET.get('product_id')
    
    comparison_list = request.session.get('comparison_list', [])
    
    if product_id in comparison_list:
        comparison_list.remove(product_id)
        request.session['comparison_list'] = comparison_list
    
    return JsonResponse({'success': True, 'count': len(comparison_list)})

def clear_comparison(request):
    request.session['comparison_list'] = []
    return JsonResponse({'success': True})

def comparison_page(request):
    comparison_list = request.session.get('comparison_list', [])
    
    if not comparison_list:
        return render(request, 'store/comparison/empty_comparison.html')
    
    products = Product.objects.filter(id__in=comparison_list, available=True)
    
    if len(products) < 2:
        return render(request, 'store/comparison/insufficient_products.html', {
            'products': products
        })
    
    # Get product specifications for comparison
    comparison_data = []
    for product in products:
        comparison_data.append({
            'product': product,
            'rating': product.reviews.aggregate(avg_rating=models.Avg('rating'))['avg_rating'] or 0,
            'review_count': product.reviews.count(),
        })
    
    return render(request, 'store/comparison/product_comparison.html', {
        'products': products,
        'comparison_data': comparison_data
    })

def get_comparison_count(request):
    comparison_list = request.session.get('comparison_list', [])
    return JsonResponse({'count': len(comparison_list)})

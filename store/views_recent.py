from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product

def recently_viewed(request):
    recently_viewed_ids = request.session.get('recently_viewed', [])
    
    if not recently_viewed_ids:
        return render(request, 'store/recent/empty_recent.html')
    
    # Get products that are still available
    products = Product.objects.filter(id__in=recently_viewed_ids, available=True)
    
    # Order products according to the recently viewed order
    product_dict = {str(product.id): product for product in products}
    ordered_products = []
    
    for product_id in recently_viewed_ids:
        if str(product_id) in product_dict:
            ordered_products.append(product_dict[str(product_id)])
    
    context = {
        'products': ordered_products,
        'total_products': len(ordered_products),
    }
    
    return render(request, 'store/recent/recently_viewed.html', context)

@csrf_exempt
def clear_recently_viewed(request):
    if request.method == 'POST':
        request.session['recently_viewed'] = []
        request.session.modified = True
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

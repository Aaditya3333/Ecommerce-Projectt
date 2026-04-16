from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Product, Wishlist
from django.core.paginator import Paginator

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).order_by('-created')
    
    # Pagination
    paginator = Paginator(wishlist_items, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_items': wishlist_items.count(),
    }
    
    return render(request, 'store/wishlist/wishlist.html', context)

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if product is already in wishlist
    if Wishlist.objects.filter(user=request.user, product=product).exists():
        return JsonResponse({'success': False, 'message': 'Product already in wishlist'})
    
    # Add to wishlist
    Wishlist.objects.create(user=request.user, product=product)
    
    return JsonResponse({'success': True, 'message': 'Product added to wishlist'})

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    try:
        wishlist_item = Wishlist.objects.get(user=request.user, product=product)
        wishlist_item.delete()
        return JsonResponse({'success': True, 'message': 'Product removed from wishlist'})
    except Wishlist.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not in wishlist'})

@login_required
def clear_wishlist(request):
    if request.method == 'POST':
        Wishlist.objects.filter(user=request.user).delete()
        return JsonResponse({'success': True, 'message': 'Wishlist cleared'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def move_to_cart(request, product_id):
    from cart.cart import Cart
    
    product = get_object_or_404(Product, id=product_id)
    
    try:
        # Remove from wishlist
        wishlist_item = Wishlist.objects.get(user=request.user, product=product)
        wishlist_item.delete()
        
        # Add to cart
        cart = Cart(request)
        cart.add(product=product)
        
        return JsonResponse({'success': True, 'message': 'Product moved to cart'})
    except Wishlist.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not in wishlist'})

def get_wishlist_count(request):
    if request.user.is_authenticated:
        count = Wishlist.objects.filter(user=request.user).count()
        return JsonResponse({'count': count})
    return JsonResponse({'count': 0})

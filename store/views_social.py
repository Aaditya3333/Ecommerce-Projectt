from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import Product, SocialShare
from django.conf import settings

def social_share(request, product_id, platform):
    product = get_object_or_404(Product, id=product_id)
    
    # Create or update social share record
    share, created = SocialShare.objects.get_or_create(
        product=product,
        platform=platform,
        defaults={'share_count': 1}
    )
    
    if not created:
        share.share_count += 1
        share.save()
    
    # Generate share URLs
    share_urls = {
        'facebook': f"https://www.facebook.com/sharer/sharer.php?u={request.build_absolute_uri(product.get_absolute_url())}",
        'twitter': f"https://twitter.com/intent/tweet?text=Check out this product: {product.name}&url={request.build_absolute_uri(product.get_absolute_url())}",
        'whatsapp': f"https://wa.me/?text=Check out this product: {product.name} - {request.build_absolute_uri(product.get_absolute_url())}",
        'instagram': f"https://www.instagram.com/",  # Instagram doesn't support direct URL sharing
        'email': f"mailto:?subject=Check out this product: {product.name}&body=I found this amazing product: {product.name} - {request.build_absolute_uri(product.get_absolute_url())}"
    }
    
    if platform in share_urls:
        return JsonResponse({
            'success': True,
            'share_url': share_urls[platform],
            'share_count': share.share_count
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid platform'})

def get_social_stats(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    shares = SocialShare.objects.filter(product=product)
    
    stats = {}
    for share in shares:
        stats[share.platform] = share.share_count
    
    return JsonResponse({'success': True, 'stats': stats})

def social_login_redirect(request, platform):
    # Social login integration would go here
    # For now, redirect to regular login
    return redirect('login')

def social_callback(request, platform):
    # Social login callback would go here
    # For now, redirect to home
    return redirect('home')

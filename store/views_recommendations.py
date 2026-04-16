from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Product, Category, Order, OrderItem, Wishlist, Review
import random
import math

def get_ai_recommendations(user, product_id=None, limit=8):
    """
    AI-powered product recommendations based on:
    1. User's browsing history
    2. Purchase history
    3. Wishlist items
    4. Similar users' preferences
    5. Product popularity and ratings
    """
    recommendations = []
    
    # Get user's recent activity
    recent_products = []
    if user.is_authenticated:
        # Get user's order history
        user_orders = Order.objects.filter(email=user.email).prefetch_related('items')
        for order in user_orders:
            for item in order.items.all():
                recent_products.append(item.product)
        
        # Get user's wishlist
        wishlist_items = Wishlist.objects.filter(user=user)
        for item in wishlist_items:
            recent_products.append(item.product)
    
    # If we have a specific product, find similar products
    if product_id:
        current_product = get_object_or_404(Product, id=product_id)
        
        # Find products in same category
        similar_products = Product.objects.filter(
            category=current_product.category
        ).exclude(id=product_id)
        
        # Find products with similar price range
        price_min = current_product.price * 0.8
        price_max = current_product.price * 1.2
        similar_products = similar_products.filter(
            price__gte=price_min,
            price__lte=price_max
        )
        
        # Sort by rating and popularity
        similar_products = similar_products.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('-avg_rating', '-review_count', '-created')
        
        recommendations = list(similar_products[:limit])
    
    # If no specific product, get general recommendations
    else:
        # Get trending products (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        trending_products = Product.objects.filter(
            available=True,
            created__gte=thirty_days_ago
        ).annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('-avg_rating', '-review_count', '-created')
        
        recommendations = list(trending_products[:limit])
    
    # If user is authenticated, add personalized recommendations
    if user.is_authenticated and recent_products:
        # Get categories user is interested in
        user_categories = set()
        for product in recent_products:
            user_categories.add(product.category)
        
        # Get top products from user's preferred categories
        personalized_products = Product.objects.filter(
            category__in=user_categories,
            available=True
        ).exclude(id__in=[p.id for p in recent_products])
        
        personalized_products = personalized_products.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('-avg_rating', '-review_count')
        
        # Mix personalized with general recommendations
        personalized_list = list(personalized_products[:limit//2])
        recommendations = recommendations[:limit//2] + personalized_list
        
        # Shuffle for variety
        random.shuffle(recommendations)
    
    return recommendations[:limit]

@login_required
def product_recommendations(request, product_id=None):
    """API endpoint to get product recommendations"""
    recommendations = get_ai_recommendations(request.user, product_id)
    
    data = []
    for product in recommendations:
        product_data = {
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'image': product.image.url if product.image else None,
            'category': product.category.name,
            'rating': product.review_set.aggregate(Avg('rating'))['rating__avg'] or 0,
            'url': f"/product/{product.id}/"
        }
        data.append(product_data)
    
    return JsonResponse({
        'success': True,
        'recommendations': data
    })

def recommendation_widget(request):
    """Render recommendation widget for templates"""
    recommendations = []
    if request.user.is_authenticated:
        recommendations = get_ai_recommendations(request.user)
    else:
        # Show trending products for anonymous users
        recommendations = get_ai_recommendations(None)
    
    return render(request, 'store/recommendations/widget.html', {
        'recommendations': recommendations
    })

def collaborative_filtering_recommendations(user, limit=8):
    """
    Advanced collaborative filtering recommendations
    Based on similar users' purchase patterns
    """
    if not user.is_authenticated:
        return []
    
    # Get user's purchased products
    user_products = set()
    user_orders = Order.objects.filter(email=user.email).prefetch_related('items')
    for order in user_orders:
        for item in order.items.all():
            user_products.add(item.product.id)
    
    # Find users who bought similar products
    similar_users = []
    for order in Order.objects.all().exclude(email=user.email):
        order_products = set()
        for item in order.items.all():
            order_products.add(item.product.id)
        
        # Calculate similarity (Jaccard similarity)
        intersection = len(user_products.intersection(order_products))
        union = len(user_products.union(order_products))
        
        if union > 0 and intersection > 0:
            similarity = intersection / union
            if similarity > 0.2:  # Threshold for similarity
                similar_users.append((order.email, similarity, order_products))
    
    # Sort by similarity
    similar_users.sort(key=lambda x: x[1], reverse=True)
    
    # Get products bought by similar users but not by current user
    recommended_products = set()
    for email, similarity, products in similar_users[:10]:  # Top 10 similar users
        recommended_products.update(products - user_products)
    
    # Get actual product objects
    products = Product.objects.filter(
        id__in=recommended_products,
        available=True
    ).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).order_by('-avg_rating', '-review_count')
    
    return list(products[:limit])

@login_required
def personalized_dashboard(request):
    """Personalized dashboard with AI recommendations"""
    # Get different types of recommendations
    trending_products = get_ai_recommendations(request.user, limit=4)
    personalized_products = collaborative_filtering_recommendations(request.user, limit=4)
    
    # Get user's shopping insights
    user_orders = Order.objects.filter(email=request.user.email)
    total_spent = sum(order.get_total() for order in user_orders)
    favorite_category = None
    
    if user_orders.exists():
        # Find user's favorite category
        category_counts = {}
        for order in user_orders:
            for item in order.items.all():
                category_name = item.product.category.name
                category_counts[category_name] = category_counts.get(category_name, 0) + 1
        
        if category_counts:
            favorite_category = max(category_counts, key=category_counts.get)
    
    context = {
        'trending_products': trending_products,
        'personalized_products': personalized_products,
        'total_orders': user_orders.count(),
        'total_spent': total_spent,
        'favorite_category': favorite_category,
    }
    
    return render(request, 'store/recommendations/dashboard.html', context)

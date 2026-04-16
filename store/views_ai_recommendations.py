from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import Product, Category, Review
from .models_ai import AIRecommendationEngine, UserBehavior, AIRecommendation, ProductEmbedding, UserEmbedding

def track_user_behavior(request):
    """Track user behavior for AI recommendations"""
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # Create behavior record
        behavior = UserBehavior.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_id=request.session.session_key or 'anonymous',
            action_type=data.get('action_type'),
            product_id=data.get('product_id'),
            category_id=data.get('category_id'),
            search_query=data.get('search_query'),
            duration=data.get('duration'),
            metadata=data.get('metadata', {})
        )
        
        # Trigger recommendation update
        if request.user.is_authenticated:
            update_user_recommendations(request.user)
        
        return JsonResponse({'success': True, 'behavior_id': behavior.id})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def update_user_recommendations(user):
    """Update AI recommendations for a user"""
    # Get active recommendation engines
    engines = AIRecommendationEngine.objects.filter(is_active=True)
    
    for engine in engines:
        if engine.algorithm == 'collaborative':
            generate_collaborative_recommendations(user, engine)
        elif engine.algorithm == 'content_based':
            generate_content_based_recommendations(user, engine)
        elif engine.algorithm == 'hybrid':
            generate_hybrid_recommendations(user, engine)

def generate_collaborative_recommendations(user, engine):
    """Generate collaborative filtering recommendations"""
    # Find similar users based on behavior patterns
    user_behaviors = UserBehavior.objects.filter(user=user).values_list('product_id', flat=True)
    similar_users = find_similar_users(user, user_behaviors)
    
    # Get products liked by similar users but not by current user
    recommendations = []
    for similar_user in similar_users[:10]:
        user_products = UserBehavior.objects.filter(
            user=similar_user,
            action_type__in=['view', 'add_to_cart', 'purchase']
        ).values_list('product_id', flat=True)
        
        for product_id in user_products:
            if product_id not in user_behaviors:
                try:
                    product = Product.objects.get(id=product_id, available=True)
                    score = calculate_collaborative_score(user, similar_user, product)
                    
                    AIRecommendation.objects.update_or_create(
                        user=user,
                        product=product,
                        engine=engine,
                        context='homepage',
                        defaults={
                            'score': score,
                            'reason': f"Users like you also liked {product.name}",
                            'metadata': {'similar_user': similar_user.id}
                        }
                    )
                except Product.DoesNotExist:
                    continue

def generate_content_based_recommendations(user, engine):
    """Generate content-based recommendations"""
    # Get user's preferred categories and products
    user_categories = UserBehavior.objects.filter(
        user=user,
        action_type__in=['view', 'add_to_cart', 'purchase']
    ).values('category_id').annotate(count=Count('id')).order_by('-count')
    
    user_products = UserBehavior.objects.filter(
        user=user,
        action_type__in=['view', 'add_to_cart', 'purchase']
    ).values_list('product_id', flat=True)
    
    # Find similar products based on content
    for category_data in user_categories[:3]:
        category_id = category_data['category_id']
        similar_products = find_similar_products_by_content(category_id, user_products)
        
        for product in similar_products[:5]:
            score = calculate_content_score(user, product, category_data['count'])
            
            AIRecommendation.objects.update_or_create(
                user=user,
                product=product,
                engine=engine,
                context='homepage',
                defaults={
                    'score': score,
                    'reason': f"Similar to products you've viewed in {product.category.name}",
                    'metadata': {'category_similarity': category_data['count']}
                }
            )

def generate_hybrid_recommendations(user, engine):
    """Generate hybrid recommendations combining multiple approaches"""
    # Get collaborative and content-based recommendations
    collab_recs = AIRecommendation.objects.filter(
        user=user,
        engine__algorithm='collaborative'
    ).order_by('-score')[:10]
    
    content_recs = AIRecommendation.objects.filter(
        user=user,
        engine__algorithm='content_based'
    ).order_by('-score')[:10]
    
    # Combine and re-score
    combined_recs = {}
    
    # Add collaborative recommendations
    for rec in collab_recs:
        combined_recs[rec.product.id] = {
            'product': rec.product,
            'collab_score': rec.score,
            'content_score': 0
        }
    
    # Add content-based recommendations
    for rec in content_recs:
        if rec.product.id in combined_recs:
            combined_recs[rec.product.id]['content_score'] = rec.score
        else:
            combined_recs[rec.product.id] = {
                'product': rec.product,
                'collab_score': 0,
                'content_score': rec.score
            }
    
    # Calculate hybrid scores
    for product_id, data in combined_recs.items():
        hybrid_score = (data['collab_score'] * 0.6) + (data['content_score'] * 0.4)
        
        AIRecommendation.objects.update_or_create(
            user=user,
            product=data['product'],
            engine=engine,
            context='homepage',
            defaults={
                'score': hybrid_score,
                'reason': f"Personalized recommendation based on your preferences",
                'metadata': {
                    'collab_score': data['collab_score'],
                    'content_score': data['content_score']
                }
            }
        )

def find_similar_users(user, user_products):
    """Find users with similar behavior patterns"""
    similar_users = []
    
    # Get users who have interacted with similar products
    for product_id in user_products:
        users = UserBehavior.objects.filter(
            product_id=product_id,
            action_type__in=['view', 'add_to_cart', 'purchase']
        ).exclude(user=user).values_list('user_id', flat=True)
        
        for user_id in users:
            if user_id not in similar_users:
                similar_users.append(user_id)
    
    return similar_users

def find_similar_products_by_content(category_id, user_products):
    """Find similar products based on content"""
    products = Product.objects.filter(
        category_id=category_id,
        available=True
    ).exclude(id__in=user_products)
    
    # Calculate similarity based on product attributes
    similar_products = []
    for product in products:
        similarity = calculate_product_similarity(product, user_products)
        if similarity > 0.3:  # Threshold for similarity
            similar_products.append(product)
    
    return sorted(similar_products, key=lambda x: calculate_product_similarity(x, user_products), reverse=True)

def calculate_collaborative_score(user, similar_user, product):
    """Calculate collaborative filtering score"""
    # Base score from similar user's interaction
    behavior = UserBehavior.objects.filter(
        user=similar_user,
        product=product
    ).first()
    
    if not behavior:
        return 0.0
    
    base_score = 0.5
    if behavior.action_type == 'purchase':
        base_score = 1.0
    elif behavior.action_type == 'add_to_cart':
        base_score = 0.8
    elif behavior.action_type == 'view':
        base_score = 0.6
    
    # Adjust for similarity strength
    similarity = calculate_user_similarity(user, similar_user)
    return base_score * similarity

def calculate_content_score(user, product, category_count):
    """Calculate content-based score"""
    score = 0.5  # Base score
    
    # Boost for category preference
    score += (category_count / 10) * 0.3
    
    # Boost for product rating
    avg_rating = product.reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    score += (avg_rating / 5) * 0.2
    
    return min(score, 1.0)

def calculate_product_similarity(product1, product2_list):
    """Calculate similarity between products"""
    # This is a simplified version - in production, use more sophisticated methods
    similarities = []
    
    for product2_id in product2_list:
        try:
            product2 = Product.objects.get(id=product2_id)
            
            # Category similarity
            category_sim = 1.0 if product1.category == product2.category else 0.0
            
            # Price similarity
            price_diff = abs(product1.price - product2.price)
            max_price = max(product1.price, product2.price)
            price_sim = 1.0 - (price_diff / max_price) if max_price > 0 else 1.0
            
            # Overall similarity
            similarity = (category_sim * 0.6) + (price_sim * 0.4)
            similarities.append(similarity)
            
        except Product.DoesNotExist:
            continue
    
    return np.mean(similarities) if similarities else 0.0

def calculate_user_similarity(user1, user2):
    """Calculate similarity between users"""
    # Get products both users have interacted with
    user1_products = set(UserBehavior.objects.filter(
        user=user1,
        action_type__in=['view', 'add_to_cart', 'purchase']
    ).values_list('product_id', flat=True))
    
    user2_products = set(UserBehavior.objects.filter(
        user=user2,
        action_type__in=['view', 'add_to_cart', 'purchase']
    ).values_list('product_id', flat=True))
    
    # Calculate Jaccard similarity
    intersection = len(user1_products.intersection(user2_products))
    union = len(user1_products.union(user2_products))
    
    return intersection / union if union > 0 else 0.0

def get_recommendations(request):
    """Get AI recommendations for the user"""
    user = request.user if request.user.is_authenticated else None
    session_id = request.session.session_key or 'anonymous'
    context = request.GET.get('context', 'homepage')
    
    recommendations = AIRecommendation.objects.filter(
        Q(user=user) | Q(session_id=session_id),
        context=context
    ).order_by('-score')[:10]
    
    data = []
    for rec in recommendations:
        data.append({
            'product_id': rec.product.id,
            'product_name': rec.product.name,
            'product_price': str(rec.product.price),
            'product_image': rec.product.image.url if rec.product.image else None,
            'score': rec.score,
            'reason': rec.reason,
            'url': f'/product/{rec.product.id}/'
        })
    
    return JsonResponse({'recommendations': data})

def trending_products_ai(request):
    """AI-powered trending products analysis"""
    # Get recent behavior data
    recent_behaviors = UserBehavior.objects.filter(
        timestamp__gte=timezone.now() - timedelta(days=7),
        action_type__in=['view', 'add_to_cart', 'purchase']
    )
    
    # Calculate trending scores
    product_scores = {}
    for behavior in recent_behaviors:
        if behavior.product:
            product_id = behavior.product.id
            if product_id not in product_scores:
                product_scores[product_id] = {
                    'views': 0,
                    'add_to_cart': 0,
                    'purchases': 0,
                    'product': behavior.product
                }
            
            if behavior.action_type == 'view':
                product_scores[product_id]['views'] += 1
            elif behavior.action_type == 'add_to_cart':
                product_scores[product_id]['add_to_cart'] += 1
            elif behavior.action_type == 'purchase':
                product_scores[product_id]['purchases'] += 1
    
    # Calculate trending score
    trending_products = []
    for product_id, data in product_scores.items():
        score = (data['views'] * 1) + (data['add_to_cart'] * 3) + (data['purchases'] * 5)
        trending_products.append({
            'product': data['product'],
            'score': score,
            'views': data['views'],
            'add_to_cart': data['add_to_cart'],
            'purchases': data['purchases']
        })
    
    # Sort by score and get top 10
    trending_products.sort(key=lambda x: x['score'], reverse=True)
    trending_products = trending_products[:10]
    
    return render(request, 'store/ai/trending_products.html', {
        'trending_products': trending_products
    })

def personalization_dashboard(request):
    """AI personalization dashboard for users"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    
    # Get user behavior insights
    recent_behaviors = UserBehavior.objects.filter(
        user=user
    ).order_by('-timestamp')[:20]
    
    # Get favorite categories
    favorite_categories = UserBehavior.objects.filter(
        user=user,
        action_type__in=['view', 'add_to_cart', 'purchase']
    ).values('category__name', 'category__id').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Get recommendations
    recommendations = AIRecommendation.objects.filter(
        user=user
    ).order_by('-score')[:10]
    
    # Calculate personalization metrics
    total_interactions = UserBehavior.objects.filter(user=user).count()
    unique_products = UserBehavior.objects.filter(user=user).values('product_id').distinct().count()
    
    context = {
        'recent_behaviors': recent_behaviors,
        'favorite_categories': favorite_categories,
        'recommendations': recommendations,
        'total_interactions': total_interactions,
        'unique_products': unique_products
    }
    
    return render(request, 'store/ai/personalization_dashboard.html', context)

@csrf_exempt
def ai_search_assistant(request):
    """AI-powered search assistant"""
    if request.method == 'POST':
        data = json.loads(request.body)
        query = data.get('query', '')
        
        # Enhanced search with AI
        products = Product.objects.filter(available=True)
        
        # Basic text search
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
        
        # Add AI scoring
        scored_products = []
        for product in products:
            score = calculate_ai_search_score(query, product)
            scored_products.append({
                'product': product,
                'score': score
            })
        
        # Sort by AI score
        scored_products.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top results
        results = []
        for item in scored_products[:10]:
            product = item['product']
            results.append({
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'image': product.image.url if product.image else None,
                'category': product.category.name,
                'score': item['score'],
                'url': f'/product/{product.id}/'
            })
        
        return JsonResponse({'results': results})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def calculate_ai_search_score(query, product):
    """Calculate AI-powered search score"""
    score = 0.0
    
    # Exact name match
    if query.lower() in product.name.lower():
        score += 1.0
    
    # Partial name match
    name_words = product.name.lower().split()
    query_words = query.lower().split()
    for word in query_words:
        for name_word in name_words:
            if word in name_word:
                score += 0.5
    
    # Description match
    if query.lower() in product.description.lower():
        score += 0.3
    
    # Category match
    if query.lower() in product.category.name.lower():
        score += 0.4
    
    # Popularity boost
    recent_views = UserBehavior.objects.filter(
        product=product,
        timestamp__gte=timezone.now() - timedelta(days=7)
    ).count()
    score += min(recent_views / 100, 0.5)
    
    # Rating boost
    avg_rating = product.reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    score += (avg_rating / 5) * 0.3
    
    return score

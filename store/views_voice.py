from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, Avg, Count
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, Category
import json
import re

def voice_search_page(request):
    """Voice search page with microphone interface"""
    return render(request, 'store/voice/voice_search.html')

def test_voice_page(request):
    """Simple test page for voice search debugging"""
    return render(request, 'store/voice/test_voice.html')

def voice_commands_page(request):
    """Voice commands page with interface for voice shopping commands"""
    return render(request, 'store/voice/voice_commands.html')

@csrf_exempt
@require_http_methods(["POST"])
def voice_search_api(request):
    """API endpoint for voice search"""
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        
        if not query:
            return JsonResponse({
                'success': False,
                'error': 'No query provided'
            })
        
        # Clean up the voice query
        cleaned_query = clean_voice_query(query)
        
        # Search products
        products = search_products_by_voice(cleaned_query)
        
        # Format results
        results = []
        for product in products:
            results.append({
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'description': product.description[:100] + '...' if len(product.description) > 100 else product.description,
                'category': product.category.name,
                'image': product.image.url if product.image else None,
                'url': f"/product/{product.id}/",
                'available': product.available
            })
        
        return JsonResponse({
            'success': True,
            'query': cleaned_query,
            'results': results,
            'total': len(results)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def clean_voice_query(query):
    """Clean and normalize voice search query"""
    # Remove common voice recognition artifacts
    query = re.sub(r'\b(um|uh|like|you know|actually|basically)\b', '', query, flags=re.IGNORECASE)
    
    # Remove extra whitespace
    query = re.sub(r'\s+', ' ', query).strip()
    
    # Handle common voice commands
    query = query.replace('show me', '').replace('find', '').replace('search for', '')
    query = query.replace('i want to buy', '').replace('i need', '').replace('looking for', '')
    
    return query.strip()

def search_products_by_voice(query):
    """Advanced product search with voice query understanding"""
    products = Product.objects.filter(available=True)
    
    # Split query into terms
    terms = query.lower().split()
    
    # Build search conditions
    search_conditions = Q()
    
    for term in terms:
        # Search in product name
        search_conditions |= Q(name__icontains=term)
        
        # Search in description
        search_conditions |= Q(description__icontains=term)
        
        # Search in category name
        search_conditions |= Q(category__name__icontains=term)
    
    # Apply search conditions
    products = products.filter(search_conditions)
    
    # Apply voice-specific enhancements
    products = enhance_voice_search_results(products, query)
    
    return products

def enhance_voice_search_results(products, query):
    """Enhance search results based on voice query patterns"""
    query_lower = query.lower()
    
    # Price-related queries
    if any(word in query_lower for word in ['cheap', 'affordable', 'budget', 'low price']):
        products = products.order_by('price')
    elif any(word in query_lower for word in ['expensive', 'premium', 'luxury', 'high end']):
        products = products.order_by('-price')
    
    # Quality-related queries
    elif any(word in query_lower for word in ['best', 'top', 'highest rated', 'popular']):
        products = products.annotate(
            avg_rating=Avg('review__rating'),
            review_count=Count('review')
        ).order_by('-avg_rating', '-review_count')
    
    # New products
    elif any(word in query_lower for word in ['new', 'latest', 'recent', 'just arrived']):
        products = products.order_by('-created')
    
    # Category-specific queries
    elif 'electronics' in query_lower:
        products = products.filter(category__name__icontains='electronics')
    elif 'clothing' in query_lower or 'fashion' in query_lower:
        products = products.filter(category__name__icontains='clothing')
    elif 'books' in query_lower:
        products = products.filter(category__name__icontains='books')
    
    return products.distinct()

@csrf_exempt
@require_http_methods(["POST"])
def voice_suggestions(request):
    """Get voice search suggestions"""
    try:
        data = json.loads(request.body)
        partial_query = data.get('query', '').strip()
        
        if len(partial_query) < 2:
            return JsonResponse({
                'success': True,
                'suggestions': []
            })
        
        # Get product name suggestions
        products = Product.objects.filter(
            available=True,
            name__icontains=partial_query
        )[:10]
        
        suggestions = []
        for product in products:
            suggestions.append({
                'name': product.name,
                'category': product.category.name,
                'url': f"/product/{product.id}/"
            })
        
        return JsonResponse({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def voice_commands(request):
    """Handle voice commands like 'add to cart', 'show wishlist'"""
    try:
        data = json.loads(request.body)
        command = data.get('command', '').strip().lower()
        
        # Parse voice commands
        if 'add to cart' in command:
            # Extract product ID or name
            product_id = extract_product_from_command(command)
            if product_id:
                # Add to cart logic here
                return JsonResponse({
                    'success': True,
                    'action': 'add_to_cart',
                    'product_id': product_id,
                    'message': 'Product added to cart'
                })
        
        elif 'show wishlist' in command or 'view wishlist' in command:
            return JsonResponse({
                'success': True,
                'action': 'navigate',
                'url': '/wishlist/',
                'message': 'Opening wishlist'
            })
        
        elif 'checkout' in command or 'buy now' in command:
            return JsonResponse({
                'success': True,
                'action': 'navigate',
                'url': '/checkout/',
                'message': 'Proceeding to checkout'
            })
        
        elif 'home' in command:
            return JsonResponse({
                'success': True,
                'action': 'navigate',
                'url': '/',
                'message': 'Going to home page'
            })
        
        else:
            return JsonResponse({
                'success': False,
                'error': 'Command not recognized'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def extract_product_from_command(command):
    """Extract product information from voice command"""
    # This is a simplified version - in production, you'd use NLP
    # For now, just return None as placeholder
    return None

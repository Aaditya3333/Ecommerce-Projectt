from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import speech_recognition as sr
import pyttsx3
from datetime import datetime
import uuid

from .models import Product, Category, Order
from .models_ai import VoiceAssistantSession, VoiceAssistantInteraction

@login_required
def voice_shopping_assistant(request):
    """Voice shopping assistant page"""
    # Create or get session
    session_id = request.session.get('voice_session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session['voice_session_id'] = session_id
    
    session, created = VoiceAssistantSession.objects.get_or_create(
        session_id=session_id,
        user=request.user,
        defaults={'started_at': timezone.now()}
    )
    
    context = {
        'session': session,
        'supported_commands': [
            'show me products under 1000 rupees',
            'find red shirts',
            'add to cart',
            'show my cart',
            'checkout',
            'search for laptops',
            'show electronics',
            'what are the trending products',
            'tell me about this product',
            'compare these products'
        ]
    }
    
    return render(request, 'store/voice/voice_shopping.html', context)

@csrf_exempt
def voice_command_processor(request):
    """Process voice commands"""
    if request.method == 'POST':
        try:
            # Get session
            session_id = request.session.get('voice_session_id')
            session = VoiceAssistantSession.objects.get(session_id=session_id)
            
            # Process audio data
            audio_data = request.FILES.get('audio')
            if not audio_data:
                return JsonResponse({'error': 'No audio data provided'}, status=400)
            
            # Convert speech to text
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_data) as source:
                audio = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio)
                except sr.UnknownValueError:
                    return JsonResponse({'error': 'Could not understand audio'}, status=400)
                except sr.RequestError:
                    return JsonResponse({'error': 'Speech recognition service error'}, status=500)
            
            # Process command
            response_data = process_voice_command(text, session, request.user)
            
            # Create interaction record
            interaction = VoiceAssistantInteraction.objects.create(
                session=session,
                user_input=text,
                intent=response_data['intent'],
                entities=response_data.get('entities', {}),
                response=response_data['response'],
                action_taken=response_data.get('action', ''),
                confidence_score=response_data.get('confidence', 0.0),
                is_successful=response_data.get('success', False)
            )
            
            # Update session stats
            session.total_interactions += 1
            if response_data.get('success', False):
                session.successful_interactions += 1
            session.save()
            
            # Generate voice response (optional)
            voice_url = None
            if response_data.get('speak_response', False):
                voice_url = generate_voice_response(response_data['response'])
            
            return JsonResponse({
                'success': True,
                'user_input': text,
                'response': response_data['response'],
                'intent': response_data['intent'],
                'action': response_data.get('action'),
                'voice_url': voice_url,
                'interaction_id': interaction.id
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def process_voice_command(text, session, user):
    """Process voice command and return response"""
    text_lower = text.lower()
    
    # Product search commands
    if 'show me' in text_lower and 'products' in text_lower:
        return handle_product_search(text_lower, user)
    
    elif 'search for' in text_lower or 'find' in text_lower:
        return handle_search_command(text_lower, user)
    
    elif 'add to cart' in text_lower:
        return handle_add_to_cart(text_lower, user)
    
    elif 'show my cart' in text_lower or 'cart' in text_lower:
        return handle_show_cart(user)
    
    elif 'checkout' in text_lower:
        return handle_checkout(user)
    
    elif 'show' in text_lower and ('electronics' in text_lower or 'clothing' in text_lower or 'books' in text_lower):
        return handle_show_category(text_lower, user)
    
    elif 'trending' in text_lower or 'popular' in text_lower:
        return handle_trending_products(user)
    
    elif 'tell me about' in text_lower or 'what is' in text_lower:
        return handle_product_info(text_lower, user)
    
    elif 'compare' in text_lower:
        return handle_compare_products(text_lower, user)
    
    elif 'help' in text_lower or 'what can you do' in text_lower:
        return handle_help_command()
    
    else:
        return {
            'intent': 'unknown',
            'response': "I'm sorry, I didn't understand that. You can ask me to show products, search for items, add to cart, or show trending products.",
            'success': False,
            'confidence': 0.3
        }

def handle_product_search(text, user):
    """Handle product search commands"""
    # Extract price range
    price_range = extract_price_range(text)
    
    # Extract product type
    product_type = extract_product_type(text)
    
    # Build query
    products = Product.objects.filter(available=True)
    
    if price_range:
        if price_range['min']:
            products = products.filter(price__gte=price_range['min'])
        if price_range['max']:
            products = products.filter(price__lte=price_range['max'])
    
    if product_type:
        products = products.filter(name__icontains=product_type)
    
    # Get results
    product_list = products[:10]
    
    if product_list:
        response = f"I found {len(product_list)} products"
        if price_range:
            response += f" under Rs.{price_range['max']}" if price_range['max'] else f" above Rs.{price_range['min']}"
        if product_type:
            response += f" matching '{product_type}'"
        response += ". Here are the top results: "
        response += ", ".join([p.name for p in product_list[:3]])
        
        return {
            'intent': 'product_search',
            'response': response,
            'action': 'show_products',
            'entities': {'price_range': price_range, 'product_type': product_type},
            'success': True,
            'confidence': 0.8
        }
    else:
        return {
            'intent': 'product_search',
            'response': "I couldn't find any products matching your criteria. Would you like me to search with different parameters?",
            'success': False,
            'confidence': 0.6
        }

def handle_search_command(text, user):
    """Handle search commands"""
    # Extract search query
    search_terms = extract_search_terms(text)
    
    if search_terms:
        products = Product.objects.filter(
            available=True,
            name__icontains=search_terms
        )[:5]
        
        if products:
            response = f"I found {len(products)} products matching '{search_terms}': "
            response += ", ".join([p.name for p in products])
            
            return {
                'intent': 'search',
                'response': response,
                'action': 'search_results',
                'entities': {'search_terms': search_terms},
                'success': True,
                'confidence': 0.8
            }
        else:
            return {
                'intent': 'search',
                'response': f"I couldn't find any products matching '{search_terms}'. Would you like to try a different search?",
                'success': False,
                'confidence': 0.6
            }
    else:
        return {
            'intent': 'search',
            'response': "What would you like me to search for?",
            'success': False,
            'confidence': 0.4
        }

def handle_add_to_cart(text, user):
    """Handle add to cart command"""
    # Extract product name
    product_name = extract_product_name(text)
    
    if product_name:
        try:
            product = Product.objects.get(name__icontains=product_name, available=True)
            # Add to cart logic would go here
            return {
                'intent': 'add_to_cart',
                'response': f"I've added {product.name} to your cart. Would you like to continue shopping or checkout?",
                'action': 'add_to_cart',
                'entities': {'product_id': product.id, 'product_name': product.name},
                'success': True,
                'confidence': 0.9
            }
        except Product.DoesNotExist:
            return {
                'intent': 'add_to_cart',
                'response': f"I couldn't find a product named '{product_name}'. Would you like me to search for it?",
                'success': False,
                'confidence': 0.5
            }
    else:
        return {
            'intent': 'add_to_cart',
            'response': "Which product would you like me to add to your cart?",
            'success': False,
            'confidence': 0.4
        }

def handle_show_cart(user):
    """Handle show cart command"""
    # Cart logic would go here
    return {
        'intent': 'show_cart',
        'response': "Your cart contains 3 items with a total of Rs.2,499. Would you like to proceed to checkout?",
        'action': 'show_cart',
        'success': True,
        'confidence': 0.9
    }

def handle_checkout(user):
    """Handle checkout command"""
    return {
        'intent': 'checkout',
        'response': "I'm ready to help you checkout. Your total is Rs.2,499. Would you like to proceed with payment?",
        'action': 'checkout',
        'success': True,
        'confidence': 0.9
    }

def handle_show_category(text, user):
    """Handle show category commands"""
    category_name = extract_category_name(text)
    
    if category_name:
        try:
            category = Category.objects.get(name__icontains=category_name)
            products = Product.objects.filter(category=category, available=True)[:5]
            
            if products:
                response = f"Here are some {category.name} products: "
                response += ", ".join([p.name for p in products])
                
                return {
                    'intent': 'show_category',
                    'response': response,
                    'action': 'show_category_products',
                    'entities': {'category_id': category.id, 'category_name': category.name},
                    'success': True,
                    'confidence': 0.8
                }
            else:
                return {
                    'intent': 'show_category',
                    'response': f"There are no products available in the {category.name} category right now.",
                    'success': False,
                    'confidence': 0.6
                }
        except Category.DoesNotExist:
            return {
                'intent': 'show_category',
                'response': f"I couldn't find the '{category_name}' category. Would you like me to show you all categories?",
                'success': False,
                'confidence': 0.5
            }
    else:
        return {
            'intent': 'show_category',
            'response': "Which category would you like me to show you?",
            'success': False,
            'confidence': 0.4
        }

def handle_trending_products(user):
    """Handle trending products command"""
    # Get trending products logic would go here
    trending = Product.objects.filter(available=True).order_by('?')[:5]
    
    response = "Here are the trending products right now: "
    response += ", ".join([p.name for p in trending])
    
    return {
        'intent': 'trending_products',
        'response': response,
        'action': 'show_trending',
        'success': True,
        'confidence': 0.8
    }

def handle_product_info(text, user):
    """Handle product information commands"""
    product_name = extract_product_name(text)
    
    if product_name:
        try:
            product = Product.objects.get(name__icontains=product_name, available=True)
            
            response = f"{product.name} costs Rs.{product.price}. "
            response += f"It belongs to the {product.category.name} category. "
            response += f"Current stock: {product.stock} items. "
            
            # Add rating info
            avg_rating = product.reviews.aggregate(avg=models.Avg('rating'))['avg']
            if avg_rating:
                response += f"Average rating: {avg_rating:.1f} out of 5 stars."
            
            return {
                'intent': 'product_info',
                'response': response,
                'action': 'product_details',
                'entities': {'product_id': product.id, 'product_name': product.name},
                'success': True,
                'confidence': 0.8
            }
        except Product.DoesNotExist:
            return {
                'intent': 'product_info',
                'response': f"I couldn't find a product named '{product_name}'. Would you like me to search for it?",
                'success': False,
                'confidence': 0.5
            }
    else:
        return {
            'intent': 'product_info',
            'response': "Which product would you like to know more about?",
            'success': False,
            'confidence': 0.4
        }

def handle_compare_products(text, user):
    """Handle product comparison commands"""
    return {
        'intent': 'compare_products',
        'response': "I can help you compare products. Please tell me which two products you'd like to compare.",
        'action': 'compare_products',
        'success': True,
        'confidence': 0.7
    }

def handle_help_command():
    """Handle help command"""
    response = "I can help you with: "
    response += "searching for products, adding items to cart, showing your cart, "
    response += "checking out, showing categories, finding trending products, "
    response += "getting product information, and comparing products. "
    response += "Just say what you'd like to do!"
    
    return {
        'intent': 'help',
        'response': response,
        'success': True,
        'confidence': 0.9
    }

# Helper functions for extracting entities
def extract_price_range(text):
    """Extract price range from text"""
    import re
    
    # Look for price patterns
    price_patterns = [
        r'under (\d+)',
        r'below (\d+)',
        r'less than (\d+)',
        r'above (\d+)',
        r'over (\d+)',
        r'more than (\d+)',
        r'between (\d+) and (\d+)',
        r'from (\d+) to (\d+)'
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 1:
                price = int(groups[0])
                if 'under' in pattern or 'below' in pattern or 'less than' in pattern:
                    return {'max': price}
                else:
                    return {'min': price}
            elif len(groups) == 2:
                return {'min': int(groups[0]), 'max': int(groups[1])}
    
    return None

def extract_product_type(text):
    """Extract product type from text"""
    product_types = ['laptop', 'phone', 'shirt', 'pants', 'shoes', 'watch', 'book', 'headphones']
    
    for product_type in product_types:
        if product_type in text:
            return product_type
    
    return None

def extract_search_terms(text):
    """Extract search terms from text"""
    # Simple extraction - in production use NLP
    if 'search for' in text:
        return text.split('search for')[-1].strip()
    elif 'find' in text:
        return text.split('find')[-1].strip()
    
    return None

def extract_product_name(text):
    """Extract product name from text"""
    # Simple extraction - in production use NLP
    if 'add to cart' in text:
        return text.split('add to cart')[-1].strip()
    elif 'tell me about' in text:
        return text.split('tell me about')[-1].strip()
    elif 'what is' in text:
        return text.split('what is')[-1].strip()
    
    return None

def extract_category_name(text):
    """Extract category name from text"""
    categories = ['electronics', 'clothing', 'books', 'shoes', 'accessories']
    
    for category in categories:
        if category in text:
            return category
    
    return None

def generate_voice_response(text):
    """Generate voice response from text"""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        
        # Save to file
        filename = f"voice_response_{timezone.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        engine.save_to_file(text, filename)
        engine.runAndWait()
        
        return f"/media/voice_responses/{filename}"
    except Exception as e:
        print(f"Error generating voice response: {e}")
        return None

def voice_session_analytics(request):
    """Voice session analytics for admin"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    # Get session statistics
    total_sessions = VoiceAssistantSession.objects.count()
    avg_interactions = VoiceAssistantSession.objects.aggregate(
        avg=models.Avg('total_interactions')
    )['avg'] or 0
    
    # Intent analysis
    intent_stats = VoiceAssistantInteraction.objects.values('intent').annotate(
        count=models.Count('id'),
        success_rate=models.Avg('is_successful')
    ).order_by('-count')
    
    # Recent sessions
    recent_sessions = VoiceAssistantSession.objects.order_by('-started_at')[:10]
    
    data = {
        'total_sessions': total_sessions,
        'avg_interactions': avg_interactions,
        'intent_stats': list(intent_stats),
        'recent_sessions': [
            {
                'session_id': session.session_id,
                'user': session.user.username if session.user else 'Anonymous',
                'total_interactions': session.total_interactions,
                'success_rate': (session.successful_interactions / session.total_interactions * 100) if session.total_interactions > 0 else 0,
                'started_at': session.started_at.isoformat()
            }
            for session in recent_sessions
        ]
    }
    
    return JsonResponse(data)

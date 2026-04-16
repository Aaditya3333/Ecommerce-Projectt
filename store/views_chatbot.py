from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
import json
import re
from .models import Product, Category, Order, OrderItem, Review, Wishlist

class AIChatbot:
    def __init__(self):
        self.intents = self.load_intents()
        self.product_keywords = self.load_product_keywords()
        self.context = {}
    
    def load_intents(self):
        """Load chatbot intents and responses"""
        return {
            'greeting': {
                'patterns': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
                'responses': [
                    "Hello! I'm your AI shopping assistant. How can I help you today?",
                    "Hi there! Welcome to Aaditya Store. What can I help you find?",
                    "Greetings! I'm here to assist with your shopping needs."
                ]
            },
            'product_search': {
                'patterns': ['find', 'search', 'looking for', 'show me', 'i want', 'need'],
                'responses': [
                    "I'll help you find the perfect product. What are you looking for?",
                    "Let me search for that. Can you tell me more about what you need?",
                    "I can help you find products. What category or item are you interested in?"
                ]
            },
            'price_inquiry': {
                'patterns': ['price', 'cost', 'how much', 'cheap', 'expensive', 'budget'],
                'responses': [
                    "I can help you find products within your budget. What's your price range?",
                    "Let me help you find products that fit your budget.",
                    "I can filter products by price. What's your preferred price range?"
                ]
            },
            'order_status': {
                'patterns': ['order', 'track', 'status', 'delivery', 'shipping'],
                'responses': [
                    "I can help you track your order. What's your order number?",
                    "Let me check your order status. Do you have your order ID?",
                    "I can help with order tracking. What's your order number?"
                ]
            },
            'recommendation': {
                'patterns': ['recommend', 'suggest', 'what should i buy', 'best', 'popular'],
                'responses': [
                    "I'd be happy to recommend some products! What are you interested in?",
                    "Let me suggest some great products for you. What category?",
                    "I can recommend products based on your preferences. What are you looking for?"
                ]
            },
            'help': {
                'patterns': ['help', 'how', 'what', 'can you', 'support'],
                'responses': [
                    "I can help you find products, track orders, get recommendations, and answer questions about our store.",
                    "I'm your AI shopping assistant! I can help with product searches, order tracking, recommendations, and more.",
                    "I can assist with finding products, checking order status, getting recommendations, and general store information."
                ]
            },
            'goodbye': {
                'patterns': ['bye', 'goodbye', 'see you', 'thanks', 'thank you'],
                'responses': [
                    "Thank you for chatting with me! Have a great day!",
                    "You're welcome! Come back anytime you need help.",
                    "Goodbye! Happy shopping at Aaditya Store!"
                ]
            }
        }
    
    def load_product_keywords(self):
        """Load product-related keywords for better understanding"""
        return {
            'electronics': ['phone', 'laptop', 'computer', 'tv', 'camera', 'headphones', 'speaker'],
            'clothing': ['shirt', 'pants', 'dress', 'shoes', 'jacket', 'coat', 't-shirt'],
            'books': ['book', 'novel', 'textbook', 'magazine', 'ebook'],
            'home': ['furniture', 'decor', 'kitchen', 'bedroom', 'living room'],
            'sports': ['fitness', 'exercise', 'gym', 'sports', 'equipment']
        }
    
    def process_message(self, message, user=None):
        """Process user message and generate response"""
        message = message.lower().strip()
        
        # Check for intents
        intent = self.detect_intent(message)
        
        if intent == 'product_search':
            return self.handle_product_search(message, user)
        elif intent == 'price_inquiry':
            return self.handle_price_inquiry(message, user)
        elif intent == 'order_status':
            return self.handle_order_status(message, user)
        elif intent == 'recommendation':
            return self.handle_recommendation(message, user)
        elif intent == 'greeting':
            return self.get_response(intent)
        elif intent == 'goodbye':
            return self.get_response(intent)
        elif intent == 'help':
            return self.get_response(intent)
        else:
            return self.handle_general_query(message, user)
    
    def detect_intent(self, message):
        """Detect user intent from message"""
        for intent, data in self.intents.items():
            for pattern in data['patterns']:
                if pattern in message:
                    return intent
        return 'general'
    
    def get_response(self, intent):
        """Get response for detected intent"""
        import random
        return random.choice(self.intents[intent]['responses'])
    
    def handle_product_search(self, message, user):
        """Handle product search queries"""
        # Extract product keywords
        category = self.extract_category(message)
        price_range = self.extract_price_range(message)
        
        products = Product.objects.filter(available=True)
        
        if category:
            products = products.filter(category__name__icontains=category)
        
        if price_range:
            min_price, max_price = price_range
            products = products.filter(price__gte=min_price, price__lte=max_price)
        
        products = products[:5]  # Limit to 5 results
        
        if products.exists():
            response = "I found these products for you:\n\n"
            for product in products:
                response += f"**{product.name}**\n"
                response += f"Price: ${product.price}\n"
                response += f"Category: {product.category.name}\n"
                response += f"[View Product](/product/{product.id}/)\n\n"
            
            response += "Would you like more details about any of these products?"
        else:
            response = "I couldn't find any products matching your search. Would you like me to help you with something else?"
        
        return response
    
    def handle_price_inquiry(self, message, user):
        """Handle price-related queries"""
        price_range = self.extract_price_range(message)
        
        if price_range:
            min_price, max_price = price_range
            products = Product.objects.filter(
                available=True,
                price__gte=min_price,
                price__lte=max_price
            )[:5]
            
            if products.exists():
                response = f"Here are products between ${min_price} and ${max_price}:\n\n"
                for product in products:
                    response += f"**{product.name}** - ${product.price}\n"
                    response += f"[View Product](/product/{product.id}/)\n\n"
            else:
                response = f"I couldn't find any products in that price range. Would you like to adjust your budget?"
        else:
            response = "I can help you find products in your price range. What's your budget?"
        
        return response
    
    def handle_order_status(self, message, user):
        """Handle order status queries"""
        if not user or not user.is_authenticated:
            return "To check your order status, please log in first."
        
        # Extract order number
        order_number = self.extract_order_number(message)
        
        if order_number:
            try:
                order = Order.objects.get(order_number=order_number, email=user.email)
                response = f"Order #{order.order_number}\n"
                response += f"Status: {order.status}\n"
                response += f"Total: ${order.total}\n"
                response += f"Created: {order.created.strftime('%B %d, %Y')}\n"
                response += f"Items: {order.items.count()}\n\n"
                response += "Is there anything else you'd like to know about your order?"
            except Order.DoesNotExist:
                response = "I couldn't find that order number. Please check and try again."
        else:
            # Get recent orders
            recent_orders = Order.objects.filter(email=user.email).order_by('-created')[:3]
            if recent_orders.exists():
                response = "Here are your recent orders:\n\n"
                for order in recent_orders:
                    response += f"Order #{order.order_number} - {order.status}\n"
                    response += f"Total: ${order.total} - {order.created.strftime('%B %d, %Y')}\n\n"
                response += "Which order would you like more details about?"
            else:
                response = "You don't have any recent orders. Would you like to browse our products?"
        
        return response
    
    def handle_recommendation(self, message, user):
        """Handle product recommendation queries"""
        category = self.extract_category(message)
        
        if user and user.is_authenticated:
            # Get personalized recommendations
            recommendations = self.get_personalized_recommendations(user, category)
        else:
            # Get general recommendations
            recommendations = self.get_general_recommendations(category)
        
        if recommendations:
            response = "Here are my recommendations for you:\n\n"
            for product in recommendations:
                response += f"**{product.name}**\n"
                response += f"Price: ${product.price}\n"
                response += f"Rating: {product.review_set.aggregate(avg=Avg('rating'))['avg'] or 0}/5\n"
                response += f"[View Product](/product/{product.id}/)\n\n"
        else:
            response = "I couldn't find any recommendations. Would you like to browse our popular products?"
        
        return response
    
    def handle_general_query(self, message, user):
        """Handle general queries"""
        # Check for store information
        if 'store' in message or 'about' in message:
            return "Aaditya Store is your premier online shopping destination with a wide range of products, competitive prices, and excellent customer service."
        
        # Check for shipping information
        if 'shipping' in message or 'delivery' in message:
            return "We offer standard shipping (5-7 business days) and express shipping (2-3 business days). Free shipping on orders over $50!"
        
        # Check for return policy
        if 'return' in message or 'refund' in message:
            return "We offer a 30-day return policy. Items must be unused and in original packaging. Contact our support team for assistance."
        
        # Check for payment methods
        if 'payment' in message or 'pay' in message:
            return "We accept credit cards, debit cards, PayPal, Apple Pay, and Google Pay for your convenience."
        
        # Default response
        return "I'm not sure I understand. Can you please rephrase your question or type 'help' for assistance?"
    
    def extract_category(self, message):
        """Extract product category from message"""
        for category, keywords in self.product_keywords.items():
            for keyword in keywords:
                if keyword in message:
                    return category
        return None
    
    def extract_price_range(self, message):
        """Extract price range from message"""
        # Look for price patterns like "$50-100", "between 50 and 100", etc.
        price_patterns = [
            r'\$(\d+)-\$(\d+)',
            r'between (\d+) and (\d+)',
            r'(\d+) to (\d+)',
            r'under (\d+)',
            r'below (\d+)',
            r'above (\d+)',
            r'over (\d+)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, message)
            if match:
                if len(match.groups()) == 2:
                    return (float(match.group(1)), float(match.group(2)))
                elif 'under' in pattern or 'below' in pattern:
                    return (0, float(match.group(1)))
                elif 'above' in pattern or 'over' in pattern:
                    return (float(match.group(1)), 999999)
        
        return None
    
    def extract_order_number(self, message):
        """Extract order number from message"""
        # Look for order number patterns like "ORD-12345" or just numbers
        order_patterns = [
            r'ORD-(\d+)',
            r'order #?(\d+)',
            r'(\d{6,8})'  # 6-8 digit numbers
        ]
        
        for pattern in order_patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1)
        
        return None
    
    def get_personalized_recommendations(self, user, category=None):
        """Get personalized recommendations for user"""
        # Get user's recent orders and wishlist
        recent_products = []
        
        # Get products from user's orders
        user_orders = Order.objects.filter(email=user.email).prefetch_related('items')
        for order in user_orders:
            for item in order.items.all():
                recent_products.append(item.product)
        
        # Get user's wishlist
        wishlist_items = Wishlist.objects.filter(user=user)
        for item in wishlist_items:
            recent_products.append(item.product)
        
        # Get products from same categories
        if recent_products:
            categories = set(product.category for product in recent_products)
            products = Product.objects.filter(category__in=categories, available=True)
        else:
            products = Product.objects.filter(available=True)
        
        if category:
            products = products.filter(category__name__icontains=category)
        
        # Sort by rating and popularity
        products = products.annotate(
            avg_rating=Avg('review__rating'),
            review_count=Count('review')
        ).order_by('-avg_rating', '-review_count')
        
        return list(products[:5])
    
    def get_general_recommendations(self, category=None):
        """Get general product recommendations"""
        products = Product.objects.filter(available=True)
        
        if category:
            products = products.filter(category__name__icontains=category)
        
        # Sort by rating and popularity
        products = products.annotate(
            avg_rating=Avg('review__rating'),
            review_count=Count('review')
        ).order_by('-avg_rating', '-review_count')
        
        return list(products[:5])

# Global chatbot instance
chatbot = AIChatbot()

@csrf_exempt
@require_http_methods(["POST"])
def chatbot_api(request):
    """API endpoint for chatbot interactions"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        session_id = data.get('session_id', '')
        
        if not message:
            return JsonResponse({
                'success': False,
                'error': 'No message provided'
            })
        
        # Process message with chatbot
        user = request.user if request.user.is_authenticated else None
        response = chatbot.process_message(message, user)
        
        # Save conversation history (optional)
        # save_conversation(session_id, message, response, user)
        
        return JsonResponse({
            'success': True,
            'response': response,
            'timestamp': timezone.now().isoformat()
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

def chatbot_page(request):
    """Chatbot page with full interface"""
    return render(request, 'store/chatbot/chatbot.html')

@login_required
def chatbot_history(request):
    """View chatbot conversation history"""
    # This would load conversation history from database
    conversations = []  # Load from database
    
    return render(request, 'store/chatbot/history.html', {
        'conversations': conversations
    })

def chatbot_analytics(request):
    """Chatbot analytics for admin"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'})
    
    # This would load chatbot analytics
    analytics = {
        'total_conversations': 0,
        'popular_intents': {},
        'satisfaction_rate': 0
    }
    
    return JsonResponse({'data': analytics})

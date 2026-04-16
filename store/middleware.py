from django.utils.deprecation import MiddlewareMixin

class RecentlyViewedMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Get recently viewed products from session
        recently_viewed = request.session.get('recently_viewed', [])
        
        # Add to context
        if hasattr(request, 'user') and request.user.is_authenticated:
            # For authenticated users, we can store more products
            max_products = 10
        else:
            # For anonymous users, store fewer products
            max_products = 5
        
        request.recently_viewed = recently_viewed[:max_products]
        
        return None
    
    def process_response(self, request, response):
        # Track product views
        if request.path.startswith('/product/') and response.status_code == 200:
            try:
                product_id = request.path.split('/')[2]
                if product_id.isdigit():
                    recently_viewed = request.session.get('recently_viewed', [])
                    
                    # Remove if already exists
                    if product_id in recently_viewed:
                        recently_viewed.remove(product_id)
                    
                    # Add to beginning
                    recently_viewed.insert(0, product_id)
                    
                    # Limit the number of stored products
                    if hasattr(request, 'user') and request.user.is_authenticated:
                        max_products = 10
                    else:
                        max_products = 5
                    
                    recently_viewed = recently_viewed[:max_products]
                    
                    # Save to session
                    request.session['recently_viewed'] = recently_viewed
                    request.session.modified = True
            except (ValueError, IndexError):
                pass
        
        return response

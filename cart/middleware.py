from .cart import Cart

class CartMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only add cart context for non-admin pages
        if not request.path.startswith('/admin/'):
            try:
                request.cart = Cart(request)
            except Exception:
                request.cart = None
        else:
            request.cart = None
        
        response = self.get_response(request)
        return response

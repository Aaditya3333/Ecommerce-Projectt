from .cart import Cart

def cart(request):
    try:
        return {'cart': Cart(request)}
    except Exception:
        return {'cart': None}

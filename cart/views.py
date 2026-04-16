from django.shortcuts import render, redirect, get_object_or_404
from .cart import Cart
from store.models import Product

def cart_detail(request):
    from .cart import Cart
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

def cart_add(request, product_id):
    from .cart import Cart
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product)
    return redirect('cart_detail')

def cart_remove(request, product_id):
    from .cart import Cart
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from cart.cart import Cart
from .models import Order, OrderItem, Product
from django.contrib import messages

@login_required
def checkout(request):
    cart = Cart(request)
    if not cart:
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart_detail')
    
    if request.method == 'POST':
        # Create order
        order = Order.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.user.email,  # Use logged-in user's email
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            postal_code=request.POST.get('postal_code'),
            city=request.POST.get('city'),
            payment_method='cod'
        )
        
        # Create order items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity']
            )
        
        # Clear cart
        cart.clear()
        
        messages.success(request, 'Order placed successfully! Your order will be delivered with cash on delivery.')
        return redirect('order_confirmation', order_id=order.id)
    
    return render(request, 'store/checkout/checkout.html', {'cart': cart})

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/checkout/order_confirmation.html', {'order': order})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Only allow user to view their own orders
    if order.email != request.user.email:
        messages.error(request, 'You can only view your own orders.')
        return redirect('profile')
    
    # Get all order items and calculate totals
    order_items = order.items.all()
    item_totals = []
    for item in order_items:
        item_total = item.price * item.quantity
        item_totals.append(item_total)
        # Add total as attribute to item for template
        item.total = item_total
    
    # Calculate order total
    order_total = sum(item_totals)
    order.total = order_total
    
    return render(request, 'store/checkout/order_detail.html', {'order': order})

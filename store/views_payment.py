from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.conf import settings
import stripe
from .models import Order, OrderItem, Product
from cart.cart import Cart

# Initialize Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', 'sk_test_placeholder')

@login_required
def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id, email=request.user.email)
    
    if order.paid:
        messages.warning(request, 'This order has already been paid for.')
        return redirect('order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'stripe_publishable_key': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', 'pk_test_placeholder'),
    }
    
    return render(request, 'store/payment/payment.html', context)

@login_required
def create_payment_intent(request, order_id):
    order = get_object_or_404(Order, id=order_id, email=request.user.email)
    
    if order.paid:
        return JsonResponse({'error': 'Order already paid'})
    
    try:
        # Calculate total amount in cents
        total_amount = int(order.get_total() * 100)
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=total_amount,
            currency='usd',
            metadata={
                'order_id': order.id,
                'user_email': request.user.email,
            },
            automatic_payment_methods={
                'enabled': True,
            },
        )
        
        return JsonResponse({
            'client_secret': intent.client_secret,
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', 'whsec_placeholder')
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = payment_intent.metadata.get('order_id')
        
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.paid = True
                order.save()
            except Order.DoesNotExist:
                pass
    
    return HttpResponse(status=200)

@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, email=request.user.email)
    
    if not order.paid:
        messages.warning(request, 'Payment not completed. Please try again.')
        return redirect('payment_page', order_id=order.id)
    
    # Clear cart after successful payment
    cart = Cart(request)
    cart.clear()
    
    return render(request, 'store/payment/payment_success.html', {'order': order})

@login_required
def payment_cancelled(request, order_id):
    order = get_object_or_404(Order, id=order_id, email=request.user.email)
    
    messages.info(request, 'Payment was cancelled. You can try again anytime.')
    return render(request, 'store/payment/payment_cancelled.html', {'order': order})

# Alternative payment methods
@login_required
def paypal_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, email=request.user.email)
    
    if order.paid:
        messages.warning(request, 'This order has already been paid for.')
        return redirect('order_detail', order_id=order.id)
    
    # PayPal integration would go here
    # For now, redirect to cash on delivery
    return redirect('order_confirmation', order_id=order.id)

@login_required
def digital_wallet_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, email=request.user.email)
    
    if order.paid:
        messages.warning(request, 'This order has already been paid for.')
        return redirect('order_detail', order_id=order.id)
    
    # Digital wallet integration would go here
    # For now, redirect to cash on delivery
    return redirect('order_confirmation', order_id=order.id)

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def send_order_confirmation_email(order):
    """Send order confirmation email to customer"""
    subject = f'Order Confirmation - Order #{order.id}'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = order.email
    
    # Load order items
    order_items = order.items.all()
    
    context = {
        'order': order,
        'order_items': order_items,
        'site_name': 'Aaditya Store',
    }
    
    # Render email templates
    text_content = render_to_string('store/emails/order_confirmation.txt', context)
    html_content = render_to_string('store/emails/order_confirmation.html', context)
    
    # Create email
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send()
        return True
    except Exception as e:
        print(f"Error sending order confirmation email: {e}")
        return False


def send_payment_confirmation_email(order):
    """Send payment confirmation email"""
    subject = f'Payment Received - Order #{order.id}'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = order.email
    
    context = {
        'order': order,
        'site_name': 'Aaditya Store',
    }
    
    text_content = render_to_string('store/emails/payment_confirmation.txt', context)
    html_content = render_to_string('store/emails/payment_confirmation.html', context)
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send()
        return True
    except Exception as e:
        print(f"Error sending payment confirmation email: {e}")
        return False


def send_shipping_notification_email(order):
    """Send shipping notification with tracking info"""
    subject = f'Your Order Has Shipped - Order #{order.id}'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = order.email
    
    context = {
        'order': order,
        'site_name': 'Aaditya Store',
    }
    
    text_content = render_to_string('store/emails/shipping_notification.txt', context)
    html_content = render_to_string('store/emails/shipping_notification.html', context)
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send()
        return True
    except Exception as e:
        print(f"Error sending shipping notification email: {e}")
        return False


def send_welcome_email(user):
    """Send welcome email to new users"""
    subject = 'Welcome to Aaditya Store!'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email
    
    context = {
        'user': user,
        'site_name': 'Aaditya Store',
    }
    
    text_content = render_to_string('store/emails/welcome.txt', context)
    html_content = render_to_string('store/emails/welcome.html', context)
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send()
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False


def send_password_reset_email(user, reset_url):
    """Send password reset email"""
    subject = 'Password Reset Request'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email
    
    context = {
        'user': user,
        'reset_url': reset_url,
        'site_name': 'Aaditya Store',
    }
    
    text_content = render_to_string('store/emails/password_reset.txt', context)
    html_content = render_to_string('store/emails/password_reset.html', context)
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send()
        return True
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False


def send_contact_reply_email(contact_message, reply_text):
    """Send reply to contact form submission"""
    subject = f'Re: {contact_message.subject}'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = contact_message.email
    
    context = {
        'contact_message': contact_message,
        'reply_text': reply_text,
        'site_name': 'Aaditya Store',
    }
    
    text_content = render_to_string('store/emails/contact_reply.txt', context)
    html_content = render_to_string('store/emails/contact_reply.html', context)
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send()
        return True
    except Exception as e:
        print(f"Error sending contact reply email: {e}")
        return False


def send_newsletter_confirmation_email(subscriber):
    """Send newsletter subscription confirmation"""
    subject = 'Newsletter Subscription Confirmed'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = subscriber.email
    
    context = {
        'subscriber': subscriber,
        'site_name': 'Aaditya Store',
    }
    
    text_content = render_to_string('store/emails/newsletter_confirm.txt', context)
    html_content = render_to_string('store/emails/newsletter_confirm.html', context)
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send()
        return True
    except Exception as e:
        print(f"Error sending newsletter confirmation: {e}")
        return False


def send_abandoned_cart_reminder(user, cart_items):
    """Send abandoned cart reminder email"""
    subject = "Don't forget your items!"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email
    
    context = {
        'user': user,
        'cart_items': cart_items,
        'site_name': 'Aaditya Store',
    }
    
    text_content = render_to_string('store/emails/abandoned_cart.txt', context)
    html_content = render_to_string('store/emails/abandoned_cart.html', context)
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send()
        return True
    except Exception as e:
        print(f"Error sending abandoned cart reminder: {e}")
        return False


def send_low_stock_alert_to_admin(product):
    """Send low stock alert to admin"""
    subject = f'Low Stock Alert: {product.name}'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = settings.ADMIN_EMAIL or settings.DEFAULT_FROM_EMAIL
    
    context = {
        'product': product,
        'site_name': 'Aaditya Store',
    }
    
    text_content = render_to_string('store/emails/low_stock_alert.txt', context)
    html_content = render_to_string('store/emails/low_stock_alert.html', context)
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send()
        return True
    except Exception as e:
        print(f"Error sending low stock alert: {e}")
        return False


def send_new_order_notification_to_admin(order):
    """Send new order notification to admin"""
    subject = f'New Order Received - #{order.id}'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = settings.ADMIN_EMAIL or settings.DEFAULT_FROM_EMAIL
    
    context = {
        'order': order,
        'order_items': order.items.all(),
        'site_name': 'Aaditya Store',
    }
    
    text_content = render_to_string('store/emails/new_order_admin.txt', context)
    html_content = render_to_string('store/emails/new_order_admin.html', context)
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send()
        return True
    except Exception as e:
        print(f"Error sending admin notification: {e}")
        return False

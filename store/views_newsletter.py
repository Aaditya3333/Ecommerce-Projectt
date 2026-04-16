from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .models import Newsletter, Product
from django.template.loader import render_to_string

def newsletter_signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required'})
        
        # Check if email already exists
        if Newsletter.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Email already subscribed'})
        
        # Create newsletter subscription
        newsletter = Newsletter.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        
        # Send welcome email
        try:
            subject = 'Welcome to Our Newsletter!'
            message = render_to_string('store/newsletter/welcome_email.html', {
                'first_name': first_name,
                'email': email
            })
            send_mail(
                subject,
                '',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                html_message=message,
                fail_silently=True
            )
        except Exception as e:
            print(f"Error sending welcome email: {e}")
        
        return JsonResponse({'success': True, 'message': 'Successfully subscribed!'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
def newsletter_unsubscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required'})
        
        try:
            newsletter = Newsletter.objects.get(email=email)
            newsletter.is_active = False
            newsletter.save()
            
            # Send confirmation email
            try:
                subject = 'Unsubscribed from Newsletter'
                message = 'You have been successfully unsubscribed from our newsletter.'
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=True
                )
            except Exception as e:
                print(f"Error sending unsubscribe email: {e}")
            
            return JsonResponse({'success': True, 'message': 'Successfully unsubscribed!'})
        except Newsletter.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Email not found'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def send_promotional_email(request):
    # Admin function to send promotional emails
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Access denied'})
    
    if request.method == 'POST':
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        
        if not subject or not content:
            return JsonResponse({'success': False, 'message': 'Subject and content are required'})
        
        # Get all active subscribers
        subscribers = Newsletter.objects.filter(is_active=True)
        
        sent_count = 0
        for subscriber in subscribers:
            try:
                message = render_to_string('store/newsletter/promotional_email.html', {
                    'first_name': subscriber.first_name,
                    'content': content,
                    'email': subscriber.email
                })
                send_mail(
                    subject,
                    '',
                    settings.DEFAULT_FROM_EMAIL,
                    [subscriber.email],
                    html_message=message,
                    fail_silently=True
                )
                sent_count += 1
            except Exception as e:
                print(f"Error sending email to {subscriber.email}: {e}")
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully sent {sent_count} emails'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def newsletter_management(request):
    # Admin panel for newsletter management
    if not request.user.is_staff:
        return render(request, 'store/analytics/access_denied.html')
    
    subscribers = Newsletter.objects.all().order_by('-created')
    
    context = {
        'subscribers': subscribers,
        'total_subscribers': subscribers.count(),
        'active_subscribers': subscribers.filter(is_active=True).count(),
    }
    
    return render(request, 'store/newsletter/management.html', context)

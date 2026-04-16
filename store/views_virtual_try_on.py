from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.utils import timezone
import json
import base64
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

from .models import Product, Category
from .models_ai import VirtualTryOn, ARProductVisualization

@login_required
def virtual_try_on_page(request, product_id):
    """Virtual try-on page for a specific product"""
    product = get_object_or_404(Product, id=product_id, available=True)
    
    # Check if product supports virtual try-on
    try_on_data = VirtualTryOn.objects.filter(
        product=product,
        user=request.user
    ).order_by('-created').first()
    
    # Check if AR visualization is available
    ar_data = ARProductVisualization.objects.filter(
        product=product,
        is_active=True
    ).first()
    
    context = {
        'product': product,
        'try_on_data': try_on_data,
        'ar_data': ar_data,
        'supported_types': ['clothing', 'accessories', 'glasses', 'makeup']
    }
    
    return render(request, 'store/virtual_try_on/try_on_page.html', context)

@csrf_exempt
def upload_user_image(request):
    """Upload user image for virtual try-on"""
    if request.method == 'POST':
        try:
            # Get image data from request
            image_data = request.POST.get('image')
            product_id = request.POST.get('product_id')
            
            if not image_data or not product_id:
                return JsonResponse({'error': 'Missing image data or product ID'}, status=400)
            
            # Decode base64 image
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            
            # Convert to image
            image_data = base64.b64decode(imgstr)
            image = Image.open(BytesIO(image_data))
            
            # Process image for better try-on results
            processed_image = process_user_image(image)
            
            # Save processed image
            image_buffer = BytesIO()
            processed_image.save(image_buffer, format='JPEG')
            image_buffer.seek(0)
            
            # Create virtual try-on record
            product = get_object_or_404(Product, id=product_id)
            try_on = VirtualTryOn.objects.create(
                product=product,
                user=request.user,
                try_on_type=get_try_on_type(product),
                user_image=ContentFile(image_buffer.read(), f'user_image_{request.user.id}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.jpg')
            )
            
            # Generate virtual try-on result
            result_url = generate_virtual_try_on_result(try_on)
            
            return JsonResponse({
                'success': True,
                'try_on_id': try_on.id,
                'result_url': result_url
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def process_user_image(image):
    """Process user image for better virtual try-on results"""
    # Convert to OpenCV format
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Face detection and alignment (simplified)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(cv_image, 1.1, 4)
    
    if len(faces) > 0:
        # Get the largest face
        face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = face
        
        # Crop and resize face region
        face_region = cv_image[y:y+h, x:x+w]
        face_region = cv2.resize(face_region, (300, 300))
        
        # Convert back to PIL
        return Image.fromarray(cv2.cvtColor(face_region, cv2.COLOR_BGR2RGB))
    
    # If no face detected, return resized original
    image = image.resize((300, 300))
    return image

def generate_virtual_try_on_result(try_on):
    """Generate virtual try-on result using AI"""
    try:
        # This is a simplified version - in production, use actual AI models
        # For now, we'll create a placeholder effect
        
        # Load user image
        user_image = Image.open(try_on.user_image.path)
        
        # Apply virtual try-on effect based on product type
        if try_on.try_on_type == 'glasses':
            result_image = apply_glasses_effect(user_image, try_on.product)
        elif try_on.try_on_type == 'clothing':
            result_image = apply_clothing_effect(user_image, try_on.product)
        elif try_on.try_on_type == 'accessories':
            result_image = apply_accessories_effect(user_image, try_on.product)
        elif try_on.try_on_type == 'makeup':
            result_image = apply_makeup_effect(user_image, try_on.product)
        else:
            result_image = user_image
        
        # Save result image
        result_buffer = BytesIO()
        result_image.save(result_buffer, format='JPEG')
        result_buffer.seek(0)
        
        try_on.result_image.save(f'result_{try_on.id}.jpg', ContentFile(result_buffer.read()), save=False)
        try_on.save()
        
        return try_on.result_image.url
        
    except Exception as e:
        print(f"Error generating virtual try-on result: {e}")
        return None

def apply_glasses_effect(user_image, product):
    """Apply virtual glasses effect"""
    # Simplified glasses overlay
    # In production, use actual computer vision models
    cv_image = cv2.cvtColor(np.array(user_image), cv2.COLOR_RGB2BGR)
    
    # Draw simple glasses shape
    cv2.rectangle(cv_image, (50, 80), (130, 110), (0, 0, 0), 2)  # Left lens
    cv2.rectangle(cv_image, (170, 80), (250, 110), (0, 0, 0), 2)  # Right lens
    cv2.line(cv_image, (130, 95), (170, 95), (0, 0, 0), 2)  # Bridge
    
    return Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))

def apply_clothing_effect(user_image, product):
    """Apply virtual clothing effect"""
    # Simplified clothing overlay
    cv_image = cv2.cvtColor(np.array(user_image), cv2.COLOR_RGB2BGR)
    
    # Draw simple shirt overlay
    cv_image[120:280, 50:250] = (100, 150, 200)  # Blue shirt
    
    return Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))

def apply_accessories_effect(user_image, product):
    """Apply virtual accessories effect"""
    # Simplified accessories overlay
    cv_image = cv2.cvtColor(np.array(user_image), cv2.COLOR_RGB2BGR)
    
    # Draw simple necklace
    cv2.ellipse(cv_image, (150, 140), (80, 20), 0, 0, 180, (255, 215, 0), 3)  # Gold necklace
    
    return Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))

def apply_makeup_effect(user_image, product):
    """Apply virtual makeup effect"""
    # Simplified makeup effect
    cv_image = cv2.cvtColor(np.array(user_image), cv2.COLOR_RGB2BGR)
    
    # Apply lipstick effect
    cv_image[140:150, 120:180] = (200, 50, 100)  # Red lipstick
    
    return Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))

def get_try_on_type(product):
    """Determine try-on type based on product category"""
    category_name = product.category.name.lower()
    
    if 'clothing' in category_name or 'shirt' in category_name or 'dress' in category_name:
        return 'clothing'
    elif 'glass' in category_name or 'spectacle' in category_name:
        return 'glasses'
    elif 'jewelry' in category_name or 'necklace' in category_name or 'ring' in category_name:
        return 'accessories'
    elif 'makeup' in category_name or 'lipstick' in category_name or 'cosmetic' in category_name:
        return 'makeup'
    else:
        return 'clothing'  # Default

@login_required
def ar_product_viewer(request, product_id):
    """AR product viewer page"""
    product = get_object_or_404(Product, id=product_id, available=True)
    ar_data = ARProductVisualization.objects.filter(
        product=product,
        is_active=True
    ).first()
    
    if not ar_data:
        return render(request, 'store/ar/not_available.html', {'product': product})
    
    context = {
        'product': product,
        'ar_data': ar_data,
        'supported_devices': ar_data.supported_devices or ['ios', 'android']
    }
    
    return render(request, 'store/ar/ar_viewer.html', context)

def ar_qr_code_generator(request, product_id):
    """Generate QR code for AR experience"""
    product = get_object_or_404(Product, id=product_id, available=True)
    ar_data = ARProductVisualization.objects.filter(
        product=product,
        is_active=True
    ).first()
    
    if not ar_data:
        return JsonResponse({'error': 'AR not available for this product'}, status=404)
    
    # Generate AR URL
    ar_url = f"{request.build_absolute_uri('/')}ar/{product.id}/"
    
    # Generate QR code (simplified - in production use proper QR library)
    qr_data = {
        'ar_url': ar_url,
        'product_name': product.name,
        'product_id': product.id
    }
    
    return JsonResponse({
        'success': True,
        'ar_url': ar_url,
        'qr_data': qr_data,
        'qr_code_url': ar_data.qr_code.url if ar_data.qr_code else None
    })

@login_required
def my_virtual_try_ons(request):
    """User's virtual try-on history"""
    try_ons = VirtualTryOn.objects.filter(
        user=request.user
    ).order_by('-created')
    
    context = {
        'try_ons': try_ons
    }
    
    return render(request, 'store/virtual_try_on/my_try_ons.html', context)

def virtual_try_on_analytics(request):
    """Virtual try-on analytics for admin"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    # Get try-on statistics
    total_try_ons = VirtualTryOn.objects.count()
    successful_try_ons = VirtualTryOn.objects.filter(result_image__isnull=False).count()
    
    # Try-ons by product
    product_stats = VirtualTryOn.objects.values(
        'product__name',
        'product__category__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Try-ons by type
    type_stats = VirtualTryOn.objects.values('try_on_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recent try-ons
    recent_try_ons = VirtualTryOn.objects.order_by('-created')[:20]
    
    data = {
        'total_try_ons': total_try_ons,
        'successful_try_ons': successful_try_ons,
        'success_rate': (successful_try_ons / total_try_ons * 100) if total_try_ons > 0 else 0,
        'product_stats': list(product_stats),
        'type_stats': list(type_stats),
        'recent_try_ons': [
            {
                'product_name': try_on.product.name,
                'user': try_on.user.username if try_on.user else 'Anonymous',
                'try_on_type': try_on.try_on_type,
                'created': try_on.created.isoformat(),
                'has_result': bool(try_on.result_image)
            }
            for try_on in recent_try_ons
        ]
    }
    
    return JsonResponse(data)

@csrf_exempt
def virtual_try_on_feedback(request):
    """Collect feedback on virtual try-on results"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            try_on_id = data.get('try_on_id')
            rating = data.get('rating')
            feedback = data.get('feedback')
            
            try_on = get_object_or_404(VirtualTryOn, id=try_on_id)
            
            # Save feedback (would need to create feedback model)
            try_on.metadata['feedback'] = {
                'rating': rating,
                'feedback': feedback,
                'timestamp': timezone.now().isoformat()
            }
            try_on.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

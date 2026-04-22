from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import (
    Product, Category, ContactMessage, Order, OrderItem, OrderStatusHistory,
    UserAddress, RecentlyViewed, Coupon, CouponUsage, Wishlist
)

def home(request):
    products = Product.objects.all()
    paginator = Paginator(products, 8)  # Show 8 products per page
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    context = {
        'product': product,
    }
    return render(request, 'store/product_detail.html', context)

def category_products(request, pk):
    category = get_object_or_404(Category, pk=pk)
    products = Product.objects.filter(category=category)
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'store/category_products.html', context)

def about(request):
    return render(request, 'store/about.html')

def services(request):
    from django.db.models import Q
    from django.core.paginator import Paginator
    
    # Get filter parameters
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort', 'newest')
    search_query = request.GET.get('q', '')
    
    # Start with all available products
    products = Product.objects.filter(available=True)
    
    # Apply filters
    if category_id:
        products = products.filter(category_id=category_id)
    
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Apply sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:  # newest
        products = products.order_by('-created')
    
    # Get categories for filter
    categories = Category.objects.all()
    
    # Pagination
    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_id,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'search_query': search_query,
        'total_products': products.count(),
    }
    
    return render(request, 'store/services.html', context)

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, 'Thank you! Your message has been sent successfully.')
            return redirect('contact')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return render(request, 'store/contact.html')


# =====================================================
# PHASE 1: ORDER TRACKING & MANAGEMENT VIEWS
# =====================================================

@login_required
def order_list(request):
    """View all orders for logged in user"""
    orders = Order.objects.filter(user=request.user).order_by('-created')
    
    # Get status filter
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    context = {
        'orders': orders,
        'status_choices': Order.ORDER_STATUS_CHOICES,
        'current_status': status_filter,
    }
    return render(request, 'store/order_list.html', context)


@login_required
def order_detail(request, order_id):
    """View detailed order information with tracking"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    status_history = order.status_history.all()
    
    context = {
        'order': order,
        'status_history': status_history,
        'order_items': order.items.all(),
    }
    return render(request, 'store/order_detail.html', context)


@login_required
def track_order(request):
    """Track order by order ID and email"""
    order = None
    error = None
    
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        email = request.POST.get('email')
        
        try:
            order = Order.objects.get(id=order_id, email=email)
        except Order.DoesNotExist:
            error = 'Order not found. Please check your Order ID and email.'
    
    context = {
        'order': order,
        'error': error,
    }
    return render(request, 'store/track_order.html', context)


@login_required
def cancel_order(request, order_id):
    """Cancel an order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Only allow cancellation for certain statuses
    if order.status in ['pending', 'confirmed']:
        if request.method == 'POST':
            reason = request.POST.get('cancellation_reason', '')
            order.status = 'cancelled'
            order.cancellation_reason = reason
            order.cancelled_at = timezone.now()
            order.save()
            
            # Add status history
            OrderStatusHistory.objects.create(
                order=order,
                status='cancelled',
                changed_by=request.user,
                notes=f'Cancelled by customer. Reason: {reason}'
            )
            
            messages.success(request, 'Your order has been cancelled successfully.')
            return redirect('order_detail', order_id=order.id)
    else:
        messages.error(request, 'This order cannot be cancelled at this stage.')
        return redirect('order_detail', order_id=order.id)
    
    return render(request, 'store/cancel_order.html', {'order': order})


@login_required
def request_return(request, order_id):
    """Request return for delivered order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status == 'delivered':
        if request.method == 'POST':
            reason = request.POST.get('return_reason', '')
            order.status = 'returned'
            order.return_reason = reason
            order.returned_at = timezone.now()
            order.save()
            
            OrderStatusHistory.objects.create(
                order=order,
                status='returned',
                changed_by=request.user,
                notes=f'Return requested. Reason: {reason}'
            )
            
            messages.success(request, 'Return request submitted successfully.')
            return redirect('order_detail', order_id=order.id)
    else:
        messages.error(request, 'Only delivered orders can be returned.')
        return redirect('order_detail', order_id=order.id)
    
    return render(request, 'store/request_return.html', {'order': order})


# =====================================================
# PHASE 2: USER ADDRESS BOOK VIEWS
# =====================================================

@login_required
def address_list(request):
    """View all saved addresses"""
    addresses = UserAddress.objects.filter(user=request.user)
    return render(request, 'store/address_list.html', {'addresses': addresses})


@login_required
def add_address(request):
    """Add new address"""
    if request.method == 'POST':
        address_type = request.POST.get('address_type', 'home')
        name = request.POST.get('name')
        recipient_name = request.POST.get('recipient_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        postal_code = request.POST.get('postal_code')
        city = request.POST.get('city')
        state = request.POST.get('state', '')
        country = request.POST.get('country', 'Nepal')
        is_default = request.POST.get('is_default') == 'on'
        
        # If this is default, remove default from others
        if is_default:
            UserAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        UserAddress.objects.create(
            user=request.user,
            address_type=address_type,
            name=name,
            recipient_name=recipient_name,
            phone=phone,
            address=address,
            postal_code=postal_code,
            city=city,
            state=state,
            country=country,
            is_default=is_default
        )
        
        messages.success(request, 'Address added successfully!')
        return redirect('address_list')
    
    return render(request, 'store/add_address.html')


@login_required
def edit_address(request, address_id):
    """Edit existing address"""
    address_obj = get_object_or_404(UserAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address_obj.address_type = request.POST.get('address_type', 'home')
        address_obj.name = request.POST.get('name')
        address_obj.recipient_name = request.POST.get('recipient_name')
        address_obj.phone = request.POST.get('phone')
        address_obj.address = request.POST.get('address')
        address_obj.postal_code = request.POST.get('postal_code')
        address_obj.city = request.POST.get('city')
        address_obj.state = request.POST.get('state', '')
        address_obj.country = request.POST.get('country', 'Nepal')
        
        is_default = request.POST.get('is_default') == 'on'
        if is_default and not address_obj.is_default:
            UserAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
        address_obj.is_default = is_default
        
        address_obj.save()
        messages.success(request, 'Address updated successfully!')
        return redirect('address_list')
    
    return render(request, 'store/edit_address.html', {'address': address_obj})


@login_required
def delete_address(request, address_id):
    """Delete address"""
    address_obj = get_object_or_404(UserAddress, id=address_id, user=request.user)
    address_obj.delete()
    messages.success(request, 'Address deleted successfully!')
    return redirect('address_list')


# =====================================================
# PHASE 2: RECENTLY VIEWED PRODUCTS
# =====================================================

@login_required
def recently_viewed(request):
    """View recently viewed products"""
    recent_views = RecentlyViewed.objects.filter(user=request.user)[:20]
    return render(request, 'store/recently_viewed.html', {'recent_views': recent_views})


def record_product_view(request, product_id):
    """Record when user views a product"""
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        RecentlyViewed.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'viewed_at': timezone.now()}
        )


# =====================================================
# PHASE 3: COUPON SYSTEM VIEWS
# =====================================================

@login_required
def apply_coupon(request):
    """Apply coupon code to cart"""
    if request.method == 'POST':
        code = request.POST.get('coupon_code', '').strip().upper()
        
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
            
            # Check validity
            if not coupon.is_valid():
                messages.error(request, 'This coupon has expired or is no longer valid.')
                return redirect('cart_detail')
            
            # Check user limit
            user_usage_count = CouponUsage.objects.filter(coupon=coupon, user=request.user).count()
            if user_usage_count >= coupon.per_user_limit:
                messages.error(request, 'You have already used this coupon.')
                return redirect('cart_detail')
            
            # Store coupon in session
            request.session['applied_coupon'] = {
                'code': coupon.code,
                'discount_type': coupon.discount_type,
                'discount_value': float(coupon.discount_value),
            }
            
            messages.success(request, f'Coupon "{coupon.code}" applied successfully!')
            
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code.')
    
    return redirect('cart_detail')


@login_required
def remove_coupon(request):
    """Remove applied coupon"""
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']
        messages.success(request, 'Coupon removed.')
    return redirect('cart_detail')


# =====================================================
# COMPREHENSIVE USER DASHBOARD
# =====================================================

@login_required
def user_dashboard(request):
    """Enhanced user dashboard with all features"""
    # Get recent orders
    recent_orders = Order.objects.filter(user=request.user).order_by('-created')[:5]
    
    # Get wishlist count
    wishlist_count = Wishlist.objects.filter(user=request.user).count()
    
    # Get address count
    address_count = UserAddress.objects.filter(user=request.user).count()
    
    # Get recently viewed
    recently_viewed_count = RecentlyViewed.objects.filter(user=request.user).count()
    
    # Get active coupons
    active_coupons = Coupon.objects.filter(is_active=True)
    
    context = {
        'recent_orders': recent_orders,
        'wishlist_count': wishlist_count,
        'address_count': address_count,
        'recently_viewed_count': recently_viewed_count,
        'active_coupons': active_coupons,
        'total_orders': Order.objects.filter(user=request.user).count(),
    }
    return render(request, 'accounts/dashboard.html', context)

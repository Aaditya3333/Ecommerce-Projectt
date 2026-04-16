from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
import json
import random
import string

from .models_loyalty import (
    LoyaltyProgram, LoyaltyTier, CustomerLoyalty, 
    PointsHistory, Reward, RewardRedemption
)
from .models import Product, Order, OrderItem

def loyalty_dashboard(request):
    """Customer loyalty dashboard"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        customer_loyalty = CustomerLoyalty.objects.get(user=request.user)
    except CustomerLoyalty.DoesNotExist:
        # Create loyalty account for new user
        program = LoyaltyProgram.objects.filter(is_active=True).first()
        if program:
            customer_loyalty = CustomerLoyalty.objects.create(
                user=request.user,
                program=program,
                total_points=program.points_for_signup,
                available_points=program.points_for_signup
            )
            # Add signup points
            PointsHistory.objects.create(
                customer_loyalty=customer_loyalty,
                points=program.points_for_signup,
                reason="Welcome bonus",
                transaction_type='earned'
            )
        else:
            customer_loyalty = None
    
    if customer_loyalty:
        # Get tier information
        current_tier = customer_loyalty.calculate_tier()
        
        # Get available rewards
        available_rewards = Reward.objects.filter(
            program=customer_loyalty.program,
            is_active=True,
            points_required__lte=customer_loyalty.available_points
        ).order_by('points_required')
        
        # Get recent activity
        recent_activity = PointsHistory.objects.filter(
            customer_loyalty=customer_loyalty
        ).order_by('-created')[:10]
        
        # Get next tier
        next_tier = LoyaltyTier.objects.filter(
            program=customer_loyalty.program,
            min_points__gt=customer_loyalty.total_points
        ).order_by('min_points').first()
        
        context = {
            'customer_loyalty': customer_loyalty,
            'current_tier': current_tier,
            'next_tier': next_tier,
            'available_rewards': available_rewards,
            'recent_activity': recent_activity,
            'points_to_next_tier': next_tier.min_points - customer_loyalty.total_points if next_tier else 0
        }
    else:
        context = {
            'customer_loyalty': None,
            'current_tier': None,
            'next_tier': None,
            'available_rewards': [],
            'recent_activity': [],
            'points_to_next_tier': 0
        }
    
    return render(request, 'store/loyalty/dashboard.html', context)

@login_required
def redeem_reward(request, reward_id):
    """Redeem a reward"""
    customer_loyalty = get_object_or_404(CustomerLoyalty, user=request.user)
    reward = get_object_or_404(Reward, id=reward_id, program=customer_loyalty.program)
    
    if customer_loyalty.available_points >= reward.points_required:
        # Check if reward is in stock
        if reward.stock_quantity <= 0:
            messages.error(request, 'This reward is currently out of stock.')
            return redirect('loyalty_dashboard')
        
        # Process redemption
        redemption = RewardRedemption.objects.create(
            customer_loyalty=customer_loyalty,
            reward=reward,
            points_used=reward.points_required,
            status='pending'
        )
        
        # Deduct points
        customer_loyalty.redeem_points(reward.points_required, f"Redeemed: {reward.name}")
        
        # Update reward stock
        reward.stock_quantity -= 1
        reward.save()
        
        # Update redemption status
        redemption.status = 'completed'
        redemption.completed_at = timezone.now()
        redemption.save()
        
        messages.success(request, f'Successfully redeemed {reward.name}!')
        
        # Handle different reward types
        if reward.discount_type == 'percentage':
            messages.info(request, f'{reward.discount_value}% discount code has been added to your account.')
        elif reward.discount_type == 'fixed':
            messages.info(request, f'Rs.{reward.discount_value} discount code has been added to your account.')
        elif reward.discount_type == 'free_shipping':
            messages.info(request, 'Free shipping code has been added to your account.')
        elif reward.discount_type == 'product' and reward.product:
            messages.info(request, f'Free {reward.product.name} has been added to your cart.')
    else:
        messages.error(request, 'Insufficient points to redeem this reward.')
    
    return redirect('loyalty_dashboard')

@login_required
def points_history(request):
    """View points history"""
    customer_loyalty = get_object_or_404(CustomerLoyalty, user=request.user)
    
    # Get points history with pagination
    history = PointsHistory.objects.filter(customer_loyalty=customer_loyalty)
    
    # Filter by transaction type
    transaction_type = request.GET.get('type')
    if transaction_type:
        history = history.filter(transaction_type=transaction_type)
    
    history = history.order_by('-created')
    
    context = {
        'customer_loyalty': customer_loyalty,
        'history': history,
        'transaction_type': transaction_type
    }
    
    return render(request, 'store/loyalty/points_history.html', context)

@login_required
def referral_program(request):
    """Referral program page"""
    customer_loyalty, created = CustomerLoyalty.objects.get_or_create(user=request.user)
    
    if not customer_loyalty.referral_code:
        # Generate unique referral code
        customer_loyalty.referral_code = generate_referral_code()
        customer_loyalty.save()
    
    # Get referral statistics
    referral_count = User.objects.filter(referrals__referred_by=request.user).count()
    points_earned = PointsHistory.objects.filter(
        customer_loyalty=customer_loyalty,
        transaction_type='earned',
        reason__icontains='referral'
    ).aggregate(total=Sum('points'))['total'] or 0
    
    context = {
        'customer_loyalty': customer_loyalty,
        'referral_count': referral_count,
        'points_earned': points_earned,
        'referral_url': f"{request.build_absolute_uri('/')}?ref={customer_loyalty.referral_code}"
    }
    
    return render(request, 'store/loyalty/referral_program.html', context)

def generate_referral_code():
    """Generate unique referral code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not CustomerLoyalty.objects.filter(referral_code=code).exists():
            return code

@login_required
def loyalty_tiers(request):
    """Display loyalty tiers information"""
    try:
        customer_loyalty = CustomerLoyalty.objects.get(user=request.user)
        program = customer_loyalty.program
    except CustomerLoyalty.DoesNotExist:
        program = LoyaltyProgram.objects.filter(is_active=True).first()
    
    if program:
        tiers = LoyaltyTier.objects.filter(program=program).order_by('min_points')
        current_tier = customer_loyalty.calculate_tier() if customer_loyalty else None
    else:
        tiers = []
        current_tier = None
    
    context = {
        'tiers': tiers,
        'current_tier': current_tier,
        'program': program
    }
    
    return render(request, 'store/loyalty/tiers.html', context)

@login_required
def earn_points_opportunities(request):
    """Show ways to earn points"""
    customer_loyalty = CustomerLoyalty.objects.get_or_create(user=request.user)[0]
    program = customer_loyalty.program
    
    opportunities = [
        {
            'action': 'Write a Review',
            'points': program.points_for_review,
            'description': 'Share your experience and earn points',
            'icon': 'fa-star'
        },
        {
            'action': 'Refer a Friend',
            'points': program.points_for_referral,
            'description': 'Invite friends and earn bonus points',
            'icon': 'fa-user-plus'
        },
        {
            'action': 'Make a Purchase',
            'points': '1 point per Rs.1 spent',
            'description': 'Earn points with every purchase',
            'icon': 'fa-shopping-cart'
        },
        {
            'action': 'Birthday Bonus',
            'points': 200,
            'description': 'Extra points on your birthday',
            'icon': 'fa-birthday-cake'
        },
        {
            'action': 'Account Anniversary',
            'points': 150,
            'description': 'Celebrate your membership anniversary',
            'icon': 'fa-calendar-check'
        }
    ]
    
    context = {
        'customer_loyalty': customer_loyalty,
        'opportunities': opportunities,
        'program': program
    }
    
    return render(request, 'store/loyalty/earn_points.html', context)

@login_required
def loyalty_api_data(request):
    """API endpoint for loyalty data"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'})
    
    customer_loyalty = CustomerLoyalty.objects.get_or_create(user=request.user)[0]
    current_tier = customer_loyalty.calculate_tier()
    
    data = {
        'total_points': customer_loyalty.total_points,
        'available_points': customer_loyalty.available_points,
        'current_tier': {
            'name': current_tier.name if current_tier else None,
            'min_points': current_tier.min_points if current_tier else 0,
            'discount_percentage': float(current_tier.discount_percentage) if current_tier else 0,
            'color': current_tier.color if current_tier else None
        } if current_tier else None,
        'next_tier_points': LoyaltyTier.objects.filter(
            program=customer_loyalty.program,
            min_points__gt=customer_loyalty.total_points
        ).order_by('min_points').first().min_points if customer_loyalty else 0
    }
    
    return JsonResponse(data)

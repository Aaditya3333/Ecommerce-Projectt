from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Product, Review
from django.forms import ModelForm
from django import forms

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'content']
        widgets = {
            'rating': forms.Select(choices=Review._meta.get_field('rating').choices, attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Review title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your review here...'}),
        }

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user already reviewed this product
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.warning(request, 'You have already reviewed this product.')
        return redirect('product_detail', pk=product.pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            
            # Check if user has purchased this product
            from store.models import Order, OrderItem
            user_orders = Order.objects.filter(email=request.user.email)
            has_purchased = OrderItem.objects.filter(
                order__in=user_orders,
                product=product
            ).exists()
            
            review.verified_purchase = has_purchased
            review.save()
            
            messages.success(request, 'Your review has been submitted successfully!')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ReviewForm()
    
    return render(request, 'store/reviews/add_review.html', {
        'form': form,
        'product': product
    })

@login_required
def mark_review_helpful(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.helpful_count += 1
    review.save()
    return redirect('product_detail', pk=review.product.pk)

def product_reviews(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product).order_by('-created')
    
    # Pagination
    paginator = Paginator(reviews, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate rating distribution
    rating_distribution = {}
    total_reviews = reviews.count()
    
    for i in range(1, 6):
        rating_distribution[i] = reviews.filter(rating=i).count()
    
    # Calculate average rating
    avg_rating = 0
    if total_reviews > 0:
        avg_rating = sum(review.rating for review in reviews) / total_reviews
    
    context = {
        'product': product,
        'page_obj': page_obj,
        'rating_distribution': rating_distribution,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews
    }
    
    return render(request, 'store/reviews/product_reviews.html', context)

from django import forms
from .models import Product, Category, Review, Newsletter

class AdvancedSearchForm(forms.Form):
    """Advanced search form with multiple filters"""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search products...',
            'autocomplete': 'off'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price',
            'step': '0.01'
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price',
            'step': '0.01'
        })
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('', 'Sort By'),
            ('name', 'Name: A-Z'),
            ('-name', 'Name: Z-A'),
            ('price', 'Price: Low to High'),
            ('-price', 'Price: High to Low'),
            ('created', 'Newest First'),
            ('-created', 'Oldest First'),
            ('-reviews__rating', 'Highest Rated'),
            ('reviews__count', 'Most Reviewed')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    in_stock = forms.BooleanField(
        required=False,
        label='In Stock Only',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class ReviewForm(forms.ModelForm):
    """Enhanced review form"""
    class Meta:
        model = Review
        fields = ['rating', 'title', 'content']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} Stars') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Review title...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with this product...'
            })
        }

class ProductQuestionForm(forms.Form):
    """Product Q&A form"""
    question = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ask a question about this product...'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email for notifications'
        })
    )

class NewsletterForm(forms.ModelForm):
    """Enhanced newsletter signup form"""
    class Meta:
        model = Newsletter
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name'
            })
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Newsletter.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('This email is already subscribed.')
        return email

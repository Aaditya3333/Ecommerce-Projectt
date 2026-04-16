from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class AIRecommendationEngine(models.Model):
    """AI recommendation engine configuration"""
    name = models.CharField(max_length=100)
    algorithm = models.CharField(max_length=50, choices=[
        ('collaborative', 'Collaborative Filtering'),
        ('content_based', 'Content-Based Filtering'),
        ('hybrid', 'Hybrid Approach'),
        ('deep_learning', 'Deep Learning Model')
    ])
    is_active = models.BooleanField(default=True)
    weight = models.FloatField(default=1.0)
    config = models.JSONField(default=dict)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AI Recommendation Engine"
        verbose_name_plural = "AI Recommendation Engines"

    def __str__(self):
        return f"{self.name} ({self.algorithm})"

class UserBehavior(models.Model):
    """Track user behavior for AI recommendations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    action_type = models.CharField(max_length=20, choices=[
        ('view', 'Product View'),
        ('add_to_cart', 'Add to Cart'),
        ('purchase', 'Purchase'),
        ('wishlist', 'Add to Wishlist'),
        ('search', 'Search Query'),
        ('click', 'Product Click')
    ])
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
    search_query = models.CharField(max_length=200, null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True, help_text="Time spent on page in seconds")
    metadata = models.JSONField(default=dict)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "User Behavior"
        verbose_name_plural = "User Behaviors"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['session_id', 'timestamp']),
            models.Index(fields=['action_type', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.user or 'Anonymous'} - {self.action_type} at {self.timestamp}"

class AIRecommendation(models.Model):
    """AI-generated recommendations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='recommendations')
    score = models.FloatField(help_text="Recommendation confidence score")
    reason = models.CharField(max_length=200, help_text="Reason for recommendation")
    engine = models.ForeignKey(AIRecommendationEngine, on_delete=models.CASCADE)
    context = models.CharField(max_length=50, choices=[
        ('homepage', 'Homepage'),
        ('product_page', 'Product Page'),
        ('cart', 'Shopping Cart'),
        ('category', 'Category Page'),
        ('search', 'Search Results')
    ])
    metadata = models.JSONField(default=dict)
    created = models.DateTimeField(auto_now_add=True)
    clicked = models.BooleanField(default=False)
    converted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "AI Recommendation"
        verbose_name_plural = "AI Recommendations"
        ordering = ['-score']
        indexes = [
            models.Index(fields=['user', 'context', 'score']),
            models.Index(fields=['session_id', 'context', 'score']),
        ]

    def __str__(self):
        return f"Recommend {self.product.name} to {self.user or 'Anonymous'}"

class ProductEmbedding(models.Model):
    """Product embeddings for AI similarity calculations"""
    product = models.OneToOneField('Product', on_delete=models.CASCADE)
    embedding_vector = models.JSONField(help_text="Product feature embedding vector")
    category_embedding = models.JSONField(help_text="Category-based embedding")
    text_embedding = models.JSONField(help_text="Text description embedding")
    visual_embedding = models.JSONField(help_text="Visual features embedding")
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product Embedding"
        verbose_name_plural = "Product Embeddings"

    def __str__(self):
        return f"Embedding for {self.product.name}"

class UserEmbedding(models.Model):
    """User embeddings for personalized recommendations"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preference_vector = models.JSONField(help_text="User preference embedding")
    behavior_vector = models.JSONField(help_text="User behavior pattern embedding")
    demographic_vector = models.JSONField(help_text="Demographic embedding")
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Embedding"
        verbose_name_plural = "User Embeddings"

    def __str__(self):
        return f"Embedding for {self.user.username}"

class AIBasedInsight(models.Model):
    """AI-generated business insights"""
    insight_type = models.CharField(max_length=50, choices=[
        ('trending_products', 'Trending Products'),
        ('customer_segments', 'Customer Segments'),
        ('market_trends', 'Market Trends'),
        ('inventory_optimization', 'Inventory Optimization'),
        ('price_optimization', 'Price Optimization'),
        ('churn_prediction', 'Churn Prediction')
    ])
    title = models.CharField(max_length=200)
    description = models.TextField()
    confidence_score = models.FloatField()
    data = models.JSONField(help_text="Insight data and visualizations")
    actionable_recommendations = models.JSONField(help_text="Actionable recommendations")
    created = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "AI Insight"
        verbose_name_plural = "AI Insights"
        ordering = ['-created']

    def __str__(self):
        return f"{self.insight_type}: {self.title}"

class VirtualTryOn(models.Model):
    """Virtual try-on feature data"""
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    try_on_type = models.CharField(max_length=20, choices=[
        ('clothing', 'Clothing'),
        ('accessories', 'Accessories'),
        ('glasses', 'Glasses'),
        ('makeup', 'Makeup')
    ])
    user_image = models.ImageField(upload_to='virtual_try_on/user_images/', null=True, blank=True)
    result_image = models.ImageField(upload_to='virtual_try_on/results/', null=True, blank=True)
    ar_model_url = models.URLField(null=True, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Virtual Try-On"
        verbose_name_plural = "Virtual Try-Ons"
        ordering = ['-created']

    def __str__(self):
        return f"Virtual try-on for {self.product.name}"

class ARProductVisualization(models.Model):
    """AR product visualization data"""
    product = models.OneToOneField('Product', on_delete=models.CASCADE)
    ar_model_file = models.FileField(upload_to='ar_models/', null=True, blank=True)
    ar_model_url = models.URLField(null=True, blank=True)
    qr_code = models.ImageField(upload_to='ar_qr_codes/', null=True, blank=True)
    ar_viewer_url = models.URLField(null=True, blank=True)
    supported_devices = models.JSONField(default=list)
    file_size = models.BigIntegerField(null=True, blank=True)
    polygon_count = models.IntegerField(null=True, blank=True)
    texture_count = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AR Product Visualization"
        verbose_name_plural = "AR Product Visualizations"

    def __str__(self):
        return f"AR model for {self.product.name}"

class VoiceAssistantSession(models.Model):
    """Voice shopping assistant sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    total_interactions = models.IntegerField(default=0)
    successful_interactions = models.IntegerField(default=0)
    intent_accuracy = models.FloatField(null=True, blank=True)
    session_data = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Voice Assistant Session"
        verbose_name_plural = "Voice Assistant Sessions"
        ordering = ['-started_at']

    def __str__(self):
        return f"Session {self.session_id} for {self.user or 'Anonymous'}"

class VoiceAssistantInteraction(models.Model):
    """Individual voice assistant interactions"""
    session = models.ForeignKey(VoiceAssistantSession, on_delete=models.CASCADE, related_name='interactions')
    user_input = models.TextField()
    intent = models.CharField(max_length=50)
    entities = models.JSONField(default=dict)
    response = models.TextField()
    action_taken = models.CharField(max_length=100, null=True, blank=True)
    confidence_score = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_successful = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Voice Assistant Interaction"
        verbose_name_plural = "Voice Assistant Interactions"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.intent} - {self.timestamp.strftime('%H:%M:%S')}"

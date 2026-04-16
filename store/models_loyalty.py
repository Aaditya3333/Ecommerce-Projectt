from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class LoyaltyProgram(models.Model):
    """Loyalty program configuration"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    points_per_rupee = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    points_for_signup = models.IntegerField(default=100)
    points_for_review = models.IntegerField(default=50)
    points_for_referral = models.IntegerField(default=500)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Loyalty Program"
        verbose_name_plural = "Loyalty Programs"

    def __str__(self):
        return self.name

class LoyaltyTier(models.Model):
    """Loyalty program tiers"""
    program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    min_points = models.IntegerField()
    max_points = models.IntegerField(null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    benefits = models.TextField(help_text="List of tier benefits")
    color = models.CharField(max_length=7, help_text="Hex color code for tier")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Loyalty Tier"
        verbose_name_plural = "Loyalty Tiers"
        ordering = ['min_points']

    def __str__(self):
        return f"{self.name} ({self.min_points}+ points)"

class CustomerLoyalty(models.Model):
    """Customer loyalty status"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE)
    tier = models.ForeignKey(LoyaltyTier, on_delete=models.SET_NULL, null=True, blank=True)
    total_points = models.IntegerField(default=0)
    available_points = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    referred_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    birthday = models.DateField(null=True, blank=True)
    anniversary_date = models.DateField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Customer Loyalty"
        verbose_name_plural = "Customer Loyalty"

    def __str__(self):
        return f"{self.user.username} - {self.total_points} points"

    def calculate_tier(self):
        """Calculate user's tier based on points"""
        tiers = LoyaltyTier.objects.filter(program=self.program).order_by('-min_points')
        for tier in tiers:
            if self.total_points >= tier.min_points:
                return tier
        return None

    def add_points(self, points, reason=""):
        """Add points to customer account"""
        self.total_points += points
        self.available_points += points
        self.save()
        
        # Create points history record
        PointsHistory.objects.create(
            customer_loyalty=self,
            points=points,
            reason=reason,
            transaction_type='earned'
        )

    def redeem_points(self, points, reason=""):
        """Redeem points from customer account"""
        if self.available_points >= points:
            self.available_points -= points
            self.save()
            
            # Create points history record
            PointsHistory.objects.create(
                customer_loyalty=self,
                points=points,
                reason=reason,
                transaction_type='redeemed'
            )
            return True
        return False

class PointsHistory(models.Model):
    """Points transaction history"""
    TRANSACTION_TYPES = [
        ('earned', 'Earned'),
        ('redeemed', 'Redeemed'),
        ('expired', 'Expired'),
        ('adjusted', 'Adjusted')
    ]

    customer_loyalty = models.ForeignKey(CustomerLoyalty, on_delete=models.CASCADE, related_name='points_history')
    points = models.IntegerField()
    reason = models.CharField(max_length=200)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Points History"
        verbose_name_plural = "Points History"
        ordering = ['-created']

    def __str__(self):
        return f"{self.customer_loyalty.user.username} - {self.transaction_type} {self.points} points"

class Reward(models.Model):
    """Available rewards for redemption"""
    program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    points_required = models.IntegerField()
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_type = models.CharField(max_length=20, choices=[
        ('percentage', 'Percentage Discount'),
        ('fixed', 'Fixed Amount'),
        ('free_shipping', 'Free Shipping'),
        ('product', 'Free Product')
    ])
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    stock_quantity = models.IntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reward"
        verbose_name_plural = "Rewards"
        ordering = ['points_required']

    def __str__(self):
        return self.name

class RewardRedemption(models.Model):
    """Track reward redemptions"""
    customer_loyalty = models.ForeignKey(CustomerLoyalty, on_delete=models.CASCADE)
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    points_used = models.IntegerField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    created = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Reward Redemption"
        verbose_name_plural = "Reward Redemptions"
        ordering = ['-created']

    def __str__(self):
        return f"{self.customer_loyalty.user.username} - {self.reward.name}"

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
User = get_user_model()



class Platform(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Placement(models.Model):
    name = models.CharField(max_length=50)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name="placements")

    class Meta:
        unique_together = ("name", "platform")

    def __str__(self):
        return f"{self.platform.name} - {self.name}"


class CustomAudience(models.Model):
    name = models.CharField(max_length=100)
    audience_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class FlexibleSpec(models.Model):
    interest_id = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=100, default="Unknown Interest")

    def __str__(self):
        return self.label


class FaceBookAdAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='ad_accounts')
    ad_account_id = models.CharField(max_length=255, null=True, blank=True)
    pixel_id = models.CharField(max_length=255, null=True, blank=True)
    facebook_page_id = models.CharField(max_length=255, null=True, blank=True)
    access_token = models.CharField(max_length=255, null=True, blank=True)
    is_bound = models.BooleanField(default=False)
    name = models.CharField(max_length=255,null=True,blank=True)
    account_name = models.CharField(max_length=255,null=True,blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    business_manager_id = models.CharField(max_length=255, null=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.name and self.user: 
            ad_account_count = FaceBookAdAccount.objects.filter(user=self.user).count()
            self.name = f"AdAccount {ad_account_count + 1}"
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.name}  for {self.account_name}"

    class Meta:
        ordering=['created_at']

class Campaign(models.Model):
    OBJECTIVES = [
        ('TRAFFIC', 'Traffic'),
        ('LEAD_GENERATION', 'Lead Generation'),
        ('CONVERSIONS', 'Conversions'),
        ('OUTCOME_TRAFFIC', 'Outcome Traffic'),
    ]
    
    BUYING_TYPES = [
        ('AUCTION', 'Auction'),
        ('RESERVED', 'Reserved'),
    ]
    EVENT_TYPE_CHOICES = [
        ('PURCHASE', 'Purchase'),
        ('VIEW_CONTENT', 'View Content'),
        ('ADD_TO_CART', 'Add to Cart'),
    ]
    BID_STRATEGIES = [
        ('LOWEST_COST_WITHOUT_CAP', 'Lowest Cost Without Cap'),
        ('LOWEST_COST_WITH_BID_CAP', 'Lowest Cost With Bid Cap'),
        ('COST_CAP', 'Cost Cap'),
    ]    
    BUDGET_OPTIMIZATION_CHOICES = [
        ('DAILY_BUDGET', 'Daily Budget'),
        ('LIFETIME_BUDGET', 'Lifetime Budget'),
    ]
    ad_account=models.ForeignKey(FaceBookAdAccount, on_delete=models.CASCADE,null=True,blank=True,related_name='campaigns')
    campaign_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    objective = models.CharField(max_length=50, choices=OBJECTIVES)
    budget_value = models.DecimalField(
        max_digits=12,  # Adjust based on your expected range
        decimal_places=2,
        default=Decimal('0.00')
    )
    budget_optimisation_type = models.CharField(max_length=50,null=True, choices=BUDGET_OPTIMIZATION_CHOICES)
    bid_strategy = models.CharField(max_length=50, choices=BID_STRATEGIES)
    buying_type = models.CharField(max_length=50, choices=BUYING_TYPES)
    pixel_id = models.CharField(max_length=255, blank=True, null=True)
    lead_form_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AdSet(models.Model):
    campaign = models.ForeignKey("Campaign", on_delete=models.CASCADE, null=True, related_name="adsets")
    name = models.CharField(max_length=255)
    facebook_page_id = models.CharField(max_length=255, null=True, blank=True)
    pixel_id = models.CharField(max_length=255, null=True, blank=True)
    objective = models.CharField(max_length=255, null=True, blank=True)
    ad_set_budget_optimization = models.CharField(
        max_length=50,
        choices=[("DAILY_BUDGET", "Daily Budget"), ("LIFETIME_BUDGET", "Lifetime Budget")],
        default="DAILY_BUDGET",
        null=True,
        blank=True,
    )
    ad_set_budget_value = models.FloatField(null=True, blank=True)
    ad_set_bid_strategy = models.CharField(
        max_length=50,
        choices=[
            ("LOWEST_COST_WITHOUT_CAP", "Lowest Cost Without Cap"),
            ("LOWEST_COST_WITH_BID_CAP", "Lowest Cost With Bid Cap"),
            ("COST_CAP", "Cost Cap"),
        ],
        default="LOWEST_COST_WITHOUT_CAP",
        null=True,
        blank=True,
    )
    bid_amount = models.FloatField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[("All", "All"), ("Male", "Male"), ("Female", "Female")],
        default="All",
        null=True,
        blank=True,
    )
    age_min = models.IntegerField(default=18, null=True, blank=True)
    age_max = models.IntegerField(default=65, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    
    custom_audiences = models.ManyToManyField("CustomAudience", related_name="ad_sets", blank=True)
    flexible_specs = models.ManyToManyField("FlexibleSpec", related_name="ad_sets", blank=True)
    placements = models.ManyToManyField("Placement", related_name="ad_sets", blank=True)

    optimization_goal = models.CharField(
        max_length=50,
        choices=[("OFFSITE_CONVERSIONS", "Offsite Conversions"), ("IMPRESSIONS", "Impressions"), ("REACH", "Reach")],
        default="OFFSITE_CONVERSIONS",
        null=True,
        blank=True,
    )
    event_type = models.CharField(
        max_length=50,
        choices=[("PURCHASE", "Purchase"), ("VIEW_CONTENT", "View Content"), ("ADD_TO_CART", "Add to Cart")],
        default="PURCHASE",
        null=True,
        blank=True,
    )
    attribution_setting = models.CharField(max_length=50, default="7d_click", null=True, blank=True)
    app_events = models.DateTimeField(null=True, blank=True)
    ad_set_end_time = models.DateTimeField(null=True, blank=True)
    is_cbo = models.BooleanField(default=False, null=True, blank=True)
    ad_account_timezone = models.CharField(max_length=255, null=True, blank=True)
    instagram_actor_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_adset_config(self):
        placements_data = self.placements.values("name", "platform__name")
        platforms = set(placement["platform__name"] for placement in placements_data if placement["platform__name"])
        
        return {
            "name": self.name,
            "campaign_id": self.campaign.campaign_id if self.campaign else None,
            "ad_account_id": self.campaign.ad_account.ad_account_id if self.campaign else None,
            "objective": self.objective,
            "budget_optimization": self.ad_set_budget_optimization,
            "budget_value": float(self.ad_set_budget_value) if self.ad_set_budget_value else None,
            "bid_strategy": self.ad_set_bid_strategy,
            "bid_amount": float(self.bid_amount) if self.bid_amount else None,
            "gender": self.gender,
            "age_min": self.age_min,
            "age_max": self.age_max,
            "location": self.location,
            "custom_audiences": list(self.custom_audiences.values("name", "audience_id")),
            "flexible_spec": list(self.flexible_specs.values("interest_id", "label")),
            "platforms": list(platforms),
            "placements": list(placements_data),
            "optimization_goal": self.optimization_goal,
            "event_type": self.event_type,
            "attribution_setting": self.attribution_setting,
            "app_events": self.app_events.isoformat() if self.app_events else None,
            "ad_set_end_time": self.ad_set_end_time.isoformat() if self.ad_set_end_time else None,
            "is_cbo": self.is_cbo,
            "ad_account_timezone": self.ad_account_timezone,
            "instagram_actor_id": self.instagram_actor_id,
        }

    def __str__(self):
        return f"{self.name} (Campaign: {self.campaign.name if self.campaign else 'No Campaign'})"

class Ad(models.Model):
    AD_STATUSES = [
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('DISAPPROVED', 'Disapproved'),
    ]
    AD_FORMATS = [
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
        ('CAROUSEL', 'Carousel'),
    ]
    adset = models.ForeignKey(AdSet, on_delete=models.CASCADE, related_name='ads')
    name = models.CharField(max_length=255)
    creative_id = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=AD_STATUSES, default='ACTIVE')
    ad_format = models.CharField(max_length=50, choices=AD_FORMATS, default='IMAGE')
    pixel_id = models.CharField(max_length=255, blank=True, null=True)
    lead_form_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class LeadForm(models.Model):
    form_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    questions = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name








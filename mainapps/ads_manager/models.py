from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Campaign(models.Model):
    OBJECTIVES = [
        ('TRAFFIC', 'Traffic'),
        ('LEAD_GENERATION', 'Lead Generation'),
        ('CONVERSIONS', 'Conversions'),
    ]
    BID_STRATEGIES = [
        ('LOWEST_COST', 'Lowest Cost'),
        ('COST_CAP', 'Cost Cap'),
    ]
    BUYING_TYPES = [
        ('AUCTION', 'Auction'),
        ('RESERVED', 'Reserved'),
    ]

    campaign_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    objective = models.CharField(max_length=50, choices=OBJECTIVES)
    budget_optimization = models.BooleanField(default=True)
    budget_value = models.IntegerField()  # Store in cents
    bid_strategy = models.CharField(max_length=50, choices=BID_STRATEGIES)
    buying_type = models.CharField(max_length=50, choices=BUYING_TYPES)
    pixel_id = models.CharField(max_length=255, blank=True, null=True)
    lead_form_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AdSet(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='adsets')
    name = models.CharField(max_length=255)
    budget_optimization = models.BooleanField(default=True)
    budget_value = models.IntegerField()  # Store in cents
    bid_strategy = models.CharField(max_length=50, choices=Campaign.BID_STRATEGIES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


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

    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
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

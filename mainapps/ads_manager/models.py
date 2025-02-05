from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.dispatch import receiver

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


class FaceBookAdAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='ad_accounts')
    ad_account_id = models.CharField(max_length=255, null=True, blank=True)
    pixel_id = models.CharField(max_length=255, null=True, blank=True)
    facebook_page_id = models.CharField(max_length=255, null=True, blank=True)
    access_token = models.CharField(max_length=255, null=True, blank=True)
    is_bound = models.BooleanField(default=False)
    name = models.CharField(max_length=255,null=True,blank=True)
    account_name = models.CharField(max_length=255,null=True,blank=True)

    business_manager_id = models.CharField(max_length=255, null=True, blank=True)


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
    account = models.ForeignKey(FaceBookAdAccount, null=True,related_name='ads', on_delete=models.CASCADE)
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








@receiver(pre_save, sender=FaceBookAdAccount)
def set_ad_account_name(sender, instance, **kwargs):
    if not instance.name:
        ad_account_count = FaceBookAdAccount.objects.filter(user=instance.user).count()
        instance.name = f"Ad Account {ad_account_count + 1}"

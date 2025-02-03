from django.db import models

class Campaign(models.Model):
    campaign_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    objective = models.CharField(max_length=255)
    budget_optimization = models.CharField(max_length=50)
    budget_value = models.FloatField()
    bid_strategy = models.CharField(max_length=50)
    buying_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class AdSet(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='adsets')
    name = models.CharField(max_length=255)
    budget_optimization = models.CharField(max_length=50)
    budget_value = models.FloatField()
    bid_strategy = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Ad(models.Model):
    user=models.ForeignKey('accounts.User', null=True,on_delete=models.CASCADE)
    adset = models.ForeignKey(AdSet, on_delete=models.CASCADE, related_name='ads')
    name = models.CharField(max_length=255)
    creative_id = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
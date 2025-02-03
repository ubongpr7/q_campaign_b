from django.db import models

# Create your models here.


class Plan(models.Model):
    stripe_price_id = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    price_per_vsl = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    vsl_limit = models.IntegerField(default=0)

    class Meta:
        ordering = ['id'] 

class StripeCustomer(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, null=True)
    stripe_customer_id = models.CharField(max_length=255)


class Subscription(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=255, null=True)
    customer = models.ForeignKey(StripeCustomer, on_delete=models.CASCADE, null=True)
    credits = models.IntegerField(default=0)
    current_period_end = models.IntegerField(default=0)


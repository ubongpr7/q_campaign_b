from django.contrib import admin
from .models import Plan,StripeCustomer,Subscription
# Register your models here.
admin.site.register(Plan)
admin.site.register(Subscription)
admin.site.register(StripeCustomer)
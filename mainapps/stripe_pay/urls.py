from django.urls import path
from . import views
app_name='stripe'

urlpatterns=[
    path('subscribe/<str:price_id>',views.subscribe,name='subscribe'),
    path('webhooks/',views.stripe_webhook,name='webhooks'),
    path("manage-subscription", views.manage_subscription, name="manage_subscription"),  # Manage subscription
    path("billing-portal", views.billing_portal, name="billing_portal"),  # Billing portal
    path("add-credits/<str:kind>", views.add_credits, name="add_credits"),  # Add credits
    path("add-credits-success", views.add_credits_success, name="add_credits_success"),  # Add credits success page
    path("add-credits-cancel", views.add_credits_cancel, name="add_credits_cancel"),  # Add credits cancel page
    path("upgrade-subscription/<str:price_id>", views.upgrade_subscription, name="upgrade_subscription"),  # Upgrade subscription
    path("downgrade-subscription", views.downgrade_subscription, name="downgrade_subscription"),  # Downgrade subscription
    path("cancel-subscription", views.cancel_subscription, name="cancel_subscription"),  # Cancel subscription
]
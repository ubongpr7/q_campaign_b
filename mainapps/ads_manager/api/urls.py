from django.urls import path
from .views import CreateAdAccountView, CreateCampaignView, GetCampaignBudgetOptimizationView

urlpatterns = [
    path('campaigns/create/', CreateCampaignView.as_view(), name='create_campaign'),
    path('get_campaign_budget_optimization/', GetCampaignBudgetOptimizationView.as_view(), name='get_campaign_budget_optimization'),
    path('ad-accounts/create/', CreateAdAccountView.as_view(), name='create-ad-account'),
]
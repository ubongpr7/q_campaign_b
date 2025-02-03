from django.urls import path
from .views import CreateCampaignView, GetCampaignBudgetOptimizationView

urlpatterns = [
    path('create_campaign/', CreateCampaignView.as_view(), name='create_campaign'),
    path('get_campaign_budget_optimization/', GetCampaignBudgetOptimizationView.as_view(), name='get_campaign_budget_optimization'),
]
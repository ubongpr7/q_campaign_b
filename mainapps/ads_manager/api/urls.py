from django.urls import path,include
from .views import (
    CreateAdAccountView,
      CreateCampaignView, 
      GetCampaignBudgetOptimizationView,
      AdAccountViewSet)
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'ad-accounts', AdAccountViewSet)  # Creates all CRUD routes

urlpatterns = [
    path('campaigns/create/', CreateCampaignView.as_view(), name='create_campaign'),
    path('get_campaign_budget_optimization/', GetCampaignBudgetOptimizationView.as_view(), name='get_campaign_budget_optimization'),
    path('ad-accounts/create/', CreateAdAccountView.as_view(), name='create-ad-account'),
    path('', include(router.urls)),  # Include API routes
]
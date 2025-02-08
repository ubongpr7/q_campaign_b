from django.urls import path,include
from .views import (
    CreateAdAccountView,
    CreateAdSetView,
      CreateCampaignView, 
      GetCampaignBudgetOptimizationView,
      AdAccountViewSet,
    PlacementListView,
    PlatformListView,
    debug_adset)
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'ad-accounts', AdAccountViewSet,basename='ad-accounts')  # Creates all CRUD routes

urlpatterns = [
    path('campaigns/create/', CreateCampaignView.as_view(), name='create_campaign'),
    path('get_campaign_budget_optimization/', GetCampaignBudgetOptimizationView.as_view(), name='get_campaign_budget_optimization'),
    path('ad-accounts/create/', CreateAdAccountView.as_view(), name='create-ad-account'),
    path('', include(router.urls)),  # Include API routes,
    path('adsets/create/', debug_adset, name='create-adset'),
    path('platforms/', PlatformListView.as_view(), name='platform-list'),
    path('placements/', PlacementListView.as_view(), name='placement-list'),
    # path("debug-adset/", debug_adset, name="debug_adset"),


]
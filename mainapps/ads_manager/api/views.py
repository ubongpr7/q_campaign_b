from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from ..models import Campaign as DBCampaign, FaceBookAdAccount, LeadForm,AdSet, Placement, Platform
import logging
from rest_framework import generics, permissions
from .serializers import AdAccountSerializer,AdSetSerializer,CampaignSerializer


from django.conf import settings
from rest_framework import viewsets, permissions
logger = logging.getLogger(__name__)
app_secret=settings.FACEBOOK_APP_SECRET
app_id=settings.FACEBOOK_APP_ID

from rest_framework import generics
from rest_framework.filters import SearchFilter
from .serializers import PlatformSerializer, PlacementSerializer

class PlatformListView(generics.ListAPIView):
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer

class PlacementListView(generics.ListAPIView):
    queryset = Placement.objects.all()
    serializer_class = PlacementSerializer
    filterset_fields = ['name', 'platform__name']
    search_fields = ['name', 'platform__name']

class CreateAdSetView(generics.CreateAPIView):
    """
    - {
    "campaign": 1,
    "name": "Test Ad Set",
    "ad_account_id": "123456789",
    "facebook_page_id": "987654321",
    "pixel_id": "654321",
    "objective": "Conversions",
    "ad_set_budget_optimization": "DAILY_BUDGET",
    "ad_set_budget_value": 100.00,
    "ad_set_bid_strategy": "LOWEST_COST_WITHOUT_CAP",
    "bid_amount": 5.00,
    "gender": "All",
    "age_min": 18,
    "age_max": 45,
    "location": "USA",
    "custom_audiences": ["audience_1", "audience_2"],
    "platforms": {"facebook": true, "instagram": false},
    "placements": {"feed": true, "story": false},
    "optimization_goal": "OFFSITE_CONVERSIONS",
    "event_type": "PURCHASE",
    "ad_set_end_time": "2025-01-01T00:00:00Z",
    "is_cbo": false
}

    """
    queryset = AdSet.objects.all()
    serializer_class = AdSetSerializer
    permission_classes = [permissions.IsAuthenticated]  

    def perform_create(self, serializer):
        print(self.request.data)
        campaign_id = self.request.data.get('campaign')  
        serializer.save(campaign_id=campaign_id)


class CreateAdAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data.copy()

        serializer = AdAccountSerializer(data=data)
        if serializer.is_valid():
            user=request.user
            serializer.save(user=user)
            access_token = serializer.validated_data.get("access_token")
            if access_token:
                user.access_token = access_token
                user.save()
            return Response(serializer.data, status=201)
        
        return Response(serializer.errors, status=400)

class AdAccountViewSet(viewsets.ModelViewSet):
    """
    API endpoints for CRUD operations on Facebook Ad Accounts.


        - HTTP Method	Endpoint	Description
            - GET	/ad-accounts/	List all ad accounts
            - POST	/ad-accounts/	Create a new ad account
            - GET	/ad-accounts/{id}/	Retrieve a single ad account
            - PUT/PATCH	//ad-accounts/{id}/	Update an ad account
            - DELETE	/ad-accounts/{id}/	Delete an ad account
    """
    serializer_class = AdAccountSerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure only logged-in users can access
    # queryset = FaceBookAdAccount.objects.all()  # ✅ Explicitly specify queryset
    def perform_create(self, serializer):
        """Override to associate the created object with the authenticated user."""
        serializer.save(user=self.request.user)
    def get_queryset(self):
        """Return only the ad accounts owned by the authenticated user."""
        return FaceBookAdAccount.objects.filter(user=self.request.user)

class CreateCampaignView(APIView):
    def post(self, request):
        try:
            data = request.data
            access_token = data.get('access_token')
            ad_account_id = data.get('ad_account_id')
            campaign_name = data.get('campaign_name')
            objective = data.get('objective')
            budget_optimization = data.get('budget_optimization')
            budget_value = data.get('budget_value')
            bid_strategy = data.get('bid_strategy')
            buying_type = data.get('buying_type')
            pixel_id = data.get('pixel_id')  # New field for pixel tracking
            lead_form_id = data.get('lead_form_id')  # New field for lead forms

            FacebookAdsApi.init(app_id, app_secret, access_token, api_version='v19.0')

            campaign_params = {
                "name": campaign_name,
                "objective": objective,
                "special_ad_categories": ["NONE"],
                "buying_type": buying_type,
            }

            if buying_type == "AUCTION":
                budget_value_cents = int(float(budget_value) * 100)
                if budget_optimization == "DAILY_BUDGET":
                    campaign_params["daily_budget"] = budget_value_cents
                elif budget_optimization == "LIFETIME_BUDGET":
                    campaign_params["lifetime_budget"] = budget_value_cents
                campaign_params["bid_strategy"] = bid_strategy

            campaign = AdAccount(ad_account_id).create_campaign(fields=[AdAccount.Field.id], params=campaign_params)
            campaign_id = campaign['id']

            db_campaign = DBCampaign.objects.create(
                campaign_id=campaign_id,
                name=campaign_name,
                objective=objective,
                budget_optimization=budget_optimization,
                budget_value=budget_value,
                bid_strategy=bid_strategy,
                buying_type=buying_type,
                pixel_id=pixel_id,  # Save pixel_id
                lead_form_id=lead_form_id,  # Save lead_form_id
            )

            serializer = CampaignSerializer(db_campaign)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error creating campaign: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class TrackConversionView(APIView):
    def post(self, request):
        try:
            data = request.data
            pixel_id = data.get('pixel_id')
            event_name = data.get('event_name')  # e.g., "Purchase", "Lead"
            event_data = data.get('event_data')  # Additional event data

            FacebookAdsApi.init(app_id, app_secret, access_token, api_version='v19.0')

            # Track the event using the Facebook Pixel
            AdAccount(pixel_id).track_event(event_name, event_data)

            return Response({"status": "success"}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error tracking conversion: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetCampaignBudgetOptimizationView(APIView):
    def post(self, request):
        try:
            data = request.data
            campaign_id = data.get('campaign_id')
            ad_account_id = data.get('ad_account_id')
            app_id = data.get('app_id')
            access_token = data.get('access_token')

            FacebookAdsApi.init(app_id, app_secret, access_token, api_version='v19.0')

            campaign = Campaign(campaign_id).api_get(fields=[
                Campaign.Field.name,
                Campaign.Field.effective_status,
                Campaign.Field.daily_budget,
                Campaign.Field.lifetime_budget,
                Campaign.Field.objective
            ])

            is_cbo = campaign.get('daily_budget') is not None or campaign.get('lifetime_budget') is not None

            return Response({
                "name": campaign.get('name'),
                "effective_status": campaign.get('effective_status'),
                "daily_budget": campaign.get('daily_budget'),
                "lifetime_budget": campaign.get('lifetime_budget'),
                "is_campaign_budget_optimization": is_cbo,
                "objective": campaign.get("objective", "OUTCOME_TRAFFIC"),
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching campaign budget optimization: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
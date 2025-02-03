from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from mainapps.ads_manager.models import Campaign as DBCampaign
from .serializers import CampaignSerializer
import logging

logger = logging.getLogger(__name__)

class CreateCampaignView(APIView):
    def post(self, request):
        try:
            data = request.data
            app_id = data.get('app_id')
            app_secret = data.get('app_secret')
            access_token = data.get('access_token')
            ad_account_id = data.get('ad_account_id')
            campaign_name = data.get('campaign_name')
            objective = data.get('objective')
            budget_optimization = data.get('budget_optimization')
            budget_value = data.get('budget_value')
            bid_strategy = data.get('bid_strategy')
            buying_type = data.get('buying_type')

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
            )

            serializer = CampaignSerializer(db_campaign)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error creating campaign: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetCampaignBudgetOptimizationView(APIView):
    def post(self, request):
        try:
            data = request.data
            campaign_id = data.get('campaign_id')
            ad_account_id = data.get('ad_account_id')
            app_id = data.get('app_id')
            app_secret = data.get('app_secret')
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
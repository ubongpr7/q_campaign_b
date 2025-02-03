import logging
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign

logger = logging.getLogger(__name__)

def get_campaign_budget_optimization(campaign_id, ad_account_id):
    try:
        campaign = Campaign(campaign_id).api_get(fields=[
            Campaign.Field.name,
            Campaign.Field.effective_status,
            Campaign.Field.daily_budget,
            Campaign.Field.lifetime_budget,
            Campaign.Field.objective
        ])
        
        is_cbo = campaign.get('daily_budget') is not None or campaign.get('lifetime_budget') is not None
        return {
            "name": campaign.get('name'),
            "effective_status": campaign.get('effective_status'),
            "daily_budget": campaign.get('daily_budget'),
            "lifetime_budget": campaign.get('lifetime_budget'),
            "is_campaign_budget_optimization": is_cbo,
            "objective": campaign.get("objective", "OUTCOME_TRAFFIC"),
        }
    except Exception as e:
        logger.error(f"Error fetching campaign details: {e}")
        return None
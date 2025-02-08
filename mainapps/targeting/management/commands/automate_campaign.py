
# import logging
# import time
# import json
# import os
# import shutil
# import tempfile
# import subprocess
# import signal
# from threading import Lock
# from datetime import datetime, timedelta
# from pytz import timezone
# import re

# # Patch eventlet to support asynchronous operations
# import eventlet
# eventlet.monkey_patch()

# # Flask-related imports
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from flask_socketio import SocketIO, emit

# # Facebook Ads SDK
# from facebook_business.api import FacebookAdsApi
# from facebook_business.adobjects.adaccount import AdAccount
# from facebook_business.adobjects.adset import AdSet
# from facebook_business.adobjects.adcreative import AdCreative
# from facebook_business.adobjects.ad import Ad
# from facebook_business.adobjects.advideo import AdVideo
# from facebook_business.adobjects.adimage import AdImage
# from facebook_business.adobjects.campaign import Campaign


# def create_campaign(name, objective, budget_optimization, budget_value, bid_strategy, buying_type, task_id, ad_account_id, app_id, app_secret, access_token, is_cbo):
#     check_cancellation(task_id)
#     try:
#         FacebookAdsApi.init(app_id, app_secret, access_token, api_version='v19.0')

#         campaign_params = {
#             "name": name,
#             "objective": objective,
#             "special_ad_categories": ["NONE"],
#             "buying_type": buying_type,
#         }

#         # Handling Auction Buying type
#         if buying_type == "AUCTION":
#             budget_value_cents = int(float(budget_value) * 100)  # Convert to cents
#             if is_cbo:
#                 campaign_params["daily_budget"] = budget_value_cents if budget_optimization == "DAILY_BUDGET" else None
#                 campaign_params["lifetime_budget"] = budget_value_cents if budget_optimization == "LIFETIME_BUDGET" else None
#                 campaign_params["bid_strategy"] = bid_strategy

#         campaign = AdAccount(ad_account_id).create_campaign(fields=[AdAccount.Field.id], params=campaign_params)
#         logging.info(f"Created campaign with ID: {campaign['id']}")
#         return campaign['id'], campaign
#     except Exception as e:
#         error_msg = f"Error creating campaign: {e}"
#         emit_error(task_id, error_msg)
#         return None, None

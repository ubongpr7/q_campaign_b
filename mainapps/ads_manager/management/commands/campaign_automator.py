# import os
# import logging
# import tempfile
# import shutil
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from django.core.management.base import BaseCommand
# from ...models import Campaign, AdSet, Ad
# from facebook_business.api import FacebookAdsApi
# from facebook_business.adobjects.adaccount import AdAccount
# from facebook_business.adobjects.adset import AdSet as FBAdSet
# from facebook_business.adobjects.adcreative import AdCreative
# from facebook_business.adobjects.ad import Ad as FBAd
# from facebook_business.adobjects.advideo import AdVideo
# from facebook_business.adobjects.adimage import AdImage

# logger = logging.getLogger(__name__)

# class Command(BaseCommand):
#     help = 'Process campaign tasks'

#     def handle(self, *args, **kwargs):
#         campaigns = Campaign.objects.filter(status__in=['PENDING', 'PROCESSING'])
#         for campaign in campaigns:
#             try:
#                 self.process_campaign(campaign)
#             except Exception as e:
#                 logger.error(f"Error processing campaign {campaign.campaign_id}: {e}")
#                 campaign.status = 'FAILED'
#                 campaign.save()

#     def process_campaign(self, campaign):
#         # Update campaign status to PROCESSING
#         campaign.status = 'PROCESSING'
#         campaign.save()

#         # Initialize Facebook Ads API
#         FacebookAdsApi.init(
#             app_id=os.getenv('FACEBOOK_APP_ID'),
#             app_secret=os.getenv('FACEBOOK_APP_SECRET'),
#             access_token=os.getenv('FACEBOOK_ACCESS_TOKEN'),
#             api_version='v19.0'
#         )

#         # Create a temporary directory for file uploads
#         temp_dir = tempfile.mkdtemp()
#         try:
#             # Process videos and images
#             self.process_media(campaign, temp_dir)
#         finally:
#             # Clean up temporary directory
#             shutil.rmtree(temp_dir, ignore_errors=True)

#         # Update campaign status to COMPLETED
#         campaign.status = 'COMPLETED'
#         campaign.save()

#     def process_media(self, campaign, temp_dir):
#         # Get all video and image files in the temporary directory
#         video_files = self.get_all_video_files(temp_dir)
#         image_files = self.get_all_image_files(temp_dir)

#         # Update campaign totals
#         campaign.total_videos = len(video_files)
#         campaign.total_images = len(image_files)
#         campaign.save()

#         # Process videos
#         if video_files:
#             self.process_videos(campaign, video_files)

#         # Process images
#         if image_files:
#             self.process_images(campaign, image_files)

#     def process_videos(self, campaign, video_files):
#         with ThreadPoolExecutor(max_workers=5) as executor:
#             futures = {executor.submit(self.upload_and_create_ad, campaign, video): video for video in video_files}
#             for future in as_completed(futures):
#                 try:
#                     future.result()
#                     campaign.processed_videos += 1
#                     campaign.progress = (campaign.processed_videos + campaign.processed_images) / (campaign.total_videos + campaign.total_images) * 100
#                     campaign.save()
#                 except Exception as e:
#                     logger.error(f"Error processing video: {e}")

#     def process_images(self, campaign, image_files):
#         with ThreadPoolExecutor(max_workers=5) as executor:
#             futures = {executor.submit(self.upload_and_create_ad, campaign, image): image for image in image_files}
#             for future in as_completed(futures):
#                 try:
#                     future.result()
#                     campaign.processed_images += 1
#                     campaign.progress = (campaign.processed_videos + campaign.processed_images) / (campaign.total_videos + campaign.total_images) * 100
#                     campaign.save()
#                 except Exception as e:
#                     logger.error(f"Error processing image: {e}")

#     def upload_and_create_ad(self, campaign, media_file):
#         # Upload media and create ad logic
#         if media_file.lower().endswith(('.mp4', '.mov', '.avi')):
#             # Upload video
#             video = AdVideo(parent_id=campaign.ad_account_id)
#             video[AdVideo.Field.filepath] = media_file
#             video.remote_create()
#             media_id = video.get_id()
#         else:
#             # Upload image
#             image = AdImage(parent_id=campaign.ad_account_id)
#             image[AdImage.Field.filename] = media_file
#             image.remote_create()
#             media_id = image[AdImage.Field.hash]

#         # Create ad creative and ad
#         ad_creative = AdCreative(parent_id=campaign.ad_account_id)
#         ad_creative_params = {
#             AdCreative.Field.name: os.path.basename(media_file),
#             AdCreative.Field.object_story_spec: {
#                 "page_id": campaign.facebook_page_id,
#                 "link_data": {
#                     "link": campaign.destination_url,
#                     "message": campaign.ad_creative_primary_text,
#                     "image_hash": media_id if media_file.lower().endswith(('.jpg', '.jpeg', '.png')) else None,
#                     "video_id": media_id if media_file.lower().endswith(('.mp4', '.mov', '.avi')) else None,
#                 }
#             }
#         }
#         ad_creative.update(ad_creative_params)
#         ad_creative.remote_create()

#         ad = FBAd(parent_id=campaign.ad_account_id)
#         ad[FBAd.Field.name] = os.path.basename(media_file)
#         ad[FBAd.Field.adset_id] = campaign.ad_set_id
#         ad[FBAd.Field.creative] = {"creative_id": ad_creative.get_id()}
#         ad[FBAd.Field.status] = "PAUSED"
#         ad.remote_create()

#     def get_all_video_files(self, directory):
#         video_files = []
#         for root, _, files in os.walk(directory):
#             for file in files:
#                 if file.lower().endswith(('.mp4', '.mov', '.avi')):
#                     video_files.append(os.path.join(root, file))
#         return video_files

#     def get_all_image_files(self, directory):
#         image_files = []
#         for root, _, files in os.walk(directory):
#             for file in files:
#                 if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
#                     image_files.append(os.path.join(root, file))
#         return image_files 
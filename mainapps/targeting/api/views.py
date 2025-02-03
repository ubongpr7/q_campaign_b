import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.customaudience import CustomAudience
from facebook_business.adobjects.targetingsearch import TargetingSearch
from facebook_business.exceptions import FacebookRequestError

logger = logging.getLogger(__name__)

class CustomAudiencesView(APIView):
    def post(self, request):
        data = request.data
        app_id = data.get('app_id')
        app_secret = data.get('app_secret')
        access_token = data.get('access_token')
        ad_account_id = data.get('ad_account_id')

        if not app_id or not app_secret or not access_token or not ad_account_id:
            logger.error("Missing required parameters: app_id, app_secret, access_token, or ad_account_id")
            return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            FacebookAdsApi.init(app_id, app_secret, access_token, api_version='v20.0')
            ad_account = AdAccount(ad_account_id)
            audiences = ad_account.get_custom_audiences(fields=[
                CustomAudience.Field.id,
                CustomAudience.Field.name,
                CustomAudience.Field.approximate_count,
            ])

            audience_list = []
            for audience in audiences:
                audience_list.append({
                    'id': audience.get('id'),
                    'name': audience.get('name'),
                    'approximate_count': audience.get('approximate_count', 'N/A'),
                })

            return Response(audience_list, status=status.HTTP_200_OK)

        except FacebookRequestError as fb_error:
            error_message = {
                "message": fb_error.api_error_message(),
                "status": fb_error.http_status(),
                "type": fb_error.api_error_type(),
            }
            logger.error(f"FacebookRequestError: {error_message}")
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"Error fetching custom audiences: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FetchCountriesView(APIView):
    def post(self, request):
        logger.debug("Received request for countries")
        data = request.data
        query = data.get('query', {})
        app_id = data.get('app_id')
        app_secret = data.get('app_secret')
        access_token = data.get('access_token')

        if not app_id or not app_secret or not access_token:
            logger.error("Missing required parameters")
            return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(query, dict):
            logger.error("Invalid query format")
            return Response({'error': 'Invalid query format'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            FacebookAdsApi.init(app_id, app_secret, access_token, api_version='v19.0')
            params = {
                'type': 'adgeolocation',
                'location_types': ['country'],
                'q': query.get('q', ''),
                'limit': query.get('limit', 1000),
            }

            search_result = TargetingSearch.search(params=params)
            serialized_results = []
            for result in search_result:
                serialized_results.append({
                    'country_code': result.get('country_code'),
                    'key': result.get('key'),
                    'name': result.get('name'),
                    'supports_city': result.get('supports_city'),
                    'supports_region': result.get('supports_region'),
                    'type': result.get('type'),
                })

            logger.debug(f"Fetched countries: {serialized_results}")
            return Response(serialized_results, status=status.HTTP_200_OK)

        except FacebookRequestError as fb_error:
            error_message = {
                "message": fb_error.api_error_message(),
                "status": fb_error.http_status(),
                "type": fb_error.api_error_type(),
            }
            logger.error(f"FacebookRequestError occurred: {error_message}")
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"Exception occurred: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AudienceInterestsView(APIView):
    def post(self, request):
        data = request.data
        ad_account_id = data.get('ad_account_id')
        access_token = data.get('access_token')
        app_id = data.get('app_id')
        app_secret = data.get('app_secret')
        query = data.get('query', {})

        if not ad_account_id or not access_token or not app_id or not app_secret:
            logger.error("Missing required parameters: ad_account_id, access_token, app_id, or app_secret")
            return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)

        q_value = query.get('q', '').strip()
        if not q_value:
            logger.error("The 'q' parameter is required for the ad interest search")
            return Response({'error': "The 'q' parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            FacebookAdsApi.init(app_id, app_secret, access_token, api_version='v20.0')
            params = {
                'type': query.get('type', 'adinterest'),
                'q': q_value,
                'limit': query.get('limit', 1000),
                'access_token': access_token,
            }

            search_result = TargetingSearch.search(params=params)
            serialized_results = [
                {
                    'audience_size_lower_bound': result.get('audience_size_lower_bound'),
                    'audience_size_upper_bound': result.get('audience_size_upper_bound'),
                    'id': result.get('id'),
                    'name': result.get('name'),
                    'path': result.get('path'),
                    'topic': result.get('topic'),
                }
                for result in search_result
            ]

            return Response(serialized_results, status=status.HTTP_200_OK)

        except FacebookRequestError as fb_error:
            error_message = {
                "message": fb_error.api_error_message(),
                "status": fb_error.http_status(),
                "type": fb_error.api_error_type(),
            }
            logger.error(f"FacebookRequestError: {error_message}")
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
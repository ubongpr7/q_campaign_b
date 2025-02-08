from rest_framework import serializers
from mainapps.ads_manager.models import Campaign, LeadForm, AdSet, Ad,FaceBookAdAccount,Platform, Placement

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'


class LeadFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadForm
        fields = '__all__'


class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = '__all__'


class AdAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceBookAdAccount
        fields = [
            'id', 'user', 'ad_account_id', 'pixel_id', 'facebook_page_id',
            'account_name', 'access_token', 'is_bound',
            'name', 'business_manager_id'
        ]
        extra_kwargs = {'user': {'read_only': True}}  # User should be set automatically

from rest_framework import serializers

class AdSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdSet
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']



class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ['id', 'name']

class PlacementSerializer(serializers.ModelSerializer):
    platform_name = serializers.CharField(source="platform.name", read_only=True)

    class Meta:
        model = Placement
        fields = ['id', 'name', 'platform', 'platform_name']

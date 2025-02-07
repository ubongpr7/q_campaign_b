from rest_framework import serializers
from mainapps.ads_manager.models import Campaign, LeadForm, AdSet, Ad,FaceBookAdAccount


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'


class LeadFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadForm
        fields = '__all__'


class AdSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdSet
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


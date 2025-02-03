from rest_framework import serializers
from mainapps.ads_manager.models import Campaign, AdSet, Ad

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'

class AdSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdSet
        fields = '__all__'

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = '__all__'
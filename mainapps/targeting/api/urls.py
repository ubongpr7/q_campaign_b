from django.urls import path
from .views import CustomAudiencesView, FetchCountriesView, AudienceInterestsView

urlpatterns = [
    path('custom_audiences/', CustomAudiencesView.as_view(), name='custom_audiences'),
    path('get_countries/', FetchCountriesView.as_view(), name='get_countries'),
    path('interests/', AudienceInterestsView.as_view(), name='interests'),
    
]

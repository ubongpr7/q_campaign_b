from django.contrib import admin
from .models import Ad,AdSet,FaceBookAdAccount,Campaign,Placement,Platform,CustomAudience

admin.site.register(Ad)
admin.site.register(AdSet)
admin.site.register(Placement)
admin.site.register(Platform)
admin.site.register(FaceBookAdAccount)
admin.site.register(CustomAudience)
admin.site.register(Campaign)
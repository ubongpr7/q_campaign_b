from django.contrib import admin
from .models import Ad,AdSet,FaceBookAdAccount,Campaign

# Register your models here.
admin.site.register(Ad)
admin.site.register(AdSet)
admin.site.register(FaceBookAdAccount)
admin.site.register(Campaign)
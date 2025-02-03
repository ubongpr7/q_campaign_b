from django.urls import path,include
from rest_framework import routers
from .views import *
router=routers.DefaultRouter()
router.register("user",AuthApi)


urlpatterns=[
    path("",include(router.urls)),
    path("login/",LoginAPIView.as_view(),name="login"),
    path("logout/",LogoutAPI.as_view(),name="logout"),
    path("register/",SignUpView.as_view(),name="register"),
    path("token/",TokenGenerator.as_view(),name="token"),
    path("api_route/",ge_route,name="api_route"),
    # path('delete_user/', DeleteUserView.as_view(), name='delete_user'),
    # path('create_user/')

]

import json
import logging
import os
import uuid
from django.conf import settings
from django.contrib.auth import (
    login as api_login,
    logout as api_logout,
    authenticate,
    get_user_model,
    tokens,
)
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


import requests
from rest_framework import (
    viewsets,
    status,
    permissions,
    generics,
)
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import (
    FormParser,
    MultiPartParser,
    JSONParser,
    FileUploadParser,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from mainapps.accounts.models import User
from mainapps.accounts.utils import send_confirmation_email, send_html_email2
from mainapps.ads_manager.models import Ad
from mainapps.stripe_pay.models import Plan, StripeCustomer, Subscription
from .serializers import *
import stripe

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os

from .serializers import ProfileSerializer

class DeleteUserView(APIView):
    # permission_classes = [IsAuthenticated]  # Ensure the user is logged in

    def delete(self, request):
        """
        Deletes the currently logged-in user and all associated data from the system,
        then logs the user out.
        """
        try:
            user = request.user  # Get the currently logged-in user

            # Use a transaction to ensure atomicity
            with transaction.atomic():
                Ad.objects.filter(user=user.id).delete()

                # Delete the user
                user.delete()

                # Log out the user after deleting the account
                logout(request)

                return Response(
                    {"message": "User and associated data deleted successfully. You have been logged out."},
                    status=status.HTTP_200_OK,
                )

        except Exception as e:
            return Response(
                {"error": "An error occurred while deleting the user", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
class AuthApi(viewsets.ModelViewSet):
    queryset=User.objects.all()
    serializer_class=MyUserSerializer
    permission_classes=[permissions.IsAuthenticated,]

class RegistrationAPI(APIView):
    
    def post(self,request):
        serializer=UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user=User.objects.get(username=request.data['username'])
        # request.session['pk']=user.pk
        # request.session["verified "]=False
        return Response({'message':f"User with the email {request.COOKIES.get('email')}  created"},status=201)
    # def get(self,request)

class LoginAPIView(APIView):
    
    def post(self,request):
        print(request.data)
        serializer=LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data["user"]
        

        return Response("Verify Your Identity",status=200)



@api_view(['GET'])
def ge_route(request):
    route=['/api/token','api/token/refresh']
    return Response(route,status=201)

        
class TokenGenerator(TokenObtainPairView):
    def post(self, request: Request, *args, **kwargs)  :
        username=request.data.get('username')
        password=request.data.get('password')
        user=authenticate(username=username,password=password)
        if user is not None:
            response=super().post(request,*args,**kwargs)
            response.status_code=200
            return response
        else:
            return Response(status=400)

class LogoutAPI(APIView):
    permission_classes=[permissions.IsAuthenticated,]
    def post(self,request):        
        response=Response()
        response.data={
            'message':'Logged Out Successfully'
        }
        response.status_code=200
        api_logout(request)
        return response
    

def verify_recaptcha_token(recaptcha_token):
    """
    Verify the reCAPTCHA token with Google's reCAPTCHA API.
    
    Args:
        recaptcha_token (str): The token from the client-side reCAPTCHA.

    Returns:
        bool: True if the token is valid, False if invalid or not provided.
    """
    if not recaptcha_token:
        print("No reCAPTCHA token provided. Skipping verification.")
        return True  # Allow requests without reCAPTCHA if not enforced
    
    secret_key = os.getenv('RECAPTCHA_SECRET_KEY')

    if not secret_key:
        print("Error: RECAPTCHA_SECRET_KEY is missing in the app configuration.")
        return False  # Fail verification if secret key is missing

    verify_url = 'https://www.google.com/recaptcha/api/siteverify'
    payload = {'secret': secret_key, 'response': recaptcha_token}
    
    try:
        response = requests.post(verify_url, data=payload)
        result = response.json()
        print(f"reCAPTCHA verification result: {result}")
        return result.get('success', False)
    except Exception as e:
        print(f"Error verifying reCAPTCHA token: {e}")
        return False




class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignUpSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            Token.objects.filter(user=user).delete()

            # Send verification email **ONLY IF session_id is missing**
            if not request.data.get("sessionId"):
                send_html_email2(
                    subject="Welcome to QuickCampaign.io – Verify Your Email",
                    message=None,
                    from_email=settings.EMAIL_HOST_USER,
                    to_email=user.email,
                    html_file="verification.html",
                    context={
                        "first_name": user.first_name,
                        "verification_url": settings.DOMAIN + reverse(
                            "accounts:verify", kwargs={"token": user.verification_token}
                        ),
                    },
                )

            return Response(
                {"message": "User created successfully", "plan": "free" if not user.subscription else "paid"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def getCreditsInSubscription(subscription):
    credits = subscription.items.latest().price.product.metadata['credits']
    return int(credits)



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def profile(request):
    user = request.user

    if request.method == 'POST':
        data = request.data
        file = request.FILES.get('profile_picture')

        user.username = data.get('username', user.username)

        if file:
            filename = default_storage.save(os.path.join('profile_pictures', file.name), ContentFile(file.read()))
            user.profile_picture = filename 

        user.save()
        return Response({'message': 'Profile updated successfully'}, status=status.HTTP_200_OK)

    serializer = ProfileSerializer(user)
    return Response({'user': serializer.data}, status=status.HTTP_200_OK)



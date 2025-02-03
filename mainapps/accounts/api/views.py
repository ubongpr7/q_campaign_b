import json
import logging
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
from mainapps.accounts.utils import send_confirmation_email, send_html_email
from mainapps.ads_manager.models import Ad
from mainapps.stripe_pay.models import Plan, StripeCustomer, Subscription
from .serializers import *
import stripe

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
    



# @method_decorator(csrf_exempt, name='dispatch')
class SignUpView(generics.CreateAPIView):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        logging.debug(f"form: {data}")
        stripe.api_key = settings.STRIPE_SEC_KEY

        checkout_session_id = data['sessionId']
        firstname = data["first_name"]
        username = data["email"]
        password = data["password"]

        logging.info(f"data: {data}")
        user = User.objects.filter(email=username).first()
        logging.info(f"user: {user}")
        if user:
            Token.objects.filter(user=user).delete()
            return Response({"error": "User already exists.",'checkout_session_id':checkout_session_id}, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_user = User.objects.create_user(
                first_name=firstname,
                username=username,
                password=password,
                email=username,
            )
            Token.objects.filter(user=new_user).delete()
            logging.info(f"new user '{new_user}' created")
        except:
            logging.error(f"new user '{username}' creation failed")
            return Response({"error": "User creation failed.",'checkout_session_id':checkout_session_id}, status=status.HTTP_400_BAD_REQUEST)
        

        if checkout_session_id is None:
            free_plan = Plan.objects.get(id=3)
            customer = stripe.Customer.create(
                email=user.email,
                name=user.first_name,
            )
            stripe_customer = StripeCustomer(
                user=user, stripe_customer_id=customer.id
            )
            stripe_customer.save()
            subscription = Subscription(
                plan=free_plan,
                hooks=free_plan.hook_limit,
                merge_credits=free_plan.hook_limit ,
                customer=stripe_customer,
                stripe_subscription_id=None
            )
            subscription.save()
            user.subscription = subscription

            verification_token = str(uuid.uuid4())
            user.verification_token = verification_token

            user.save()

            send_html_email(
                subject='Welcome to QuickCampaign.io – Verify Your Email To Continue',
                message=None,
                from_email=settings.EMAIL_HOST_USER,
                to_email=user.email,
                html_file='verification.html',
                context={
                'first_name':
                    user.first_name,
                'verification_url':
                    settings.DOMAIN
                    + reverse('accounts:verify', kwargs={'token': verification_token}),
                },
            )
            return Response({'plan':'free','success':True}, status=status.HTTP_201_CREATED)

        else:
            checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)
            stripe_customer_id = checkout_session.customer

            customer_id = 0
            try:
                customer = StripeCustomer.objects.get(
                stripe_customer_id=stripe_customer_id
                )

                if customer is not None:
                    customer.user = user
                    customer.save()

                customer_id = customer.id
            except StripeCustomer.DoesNotExist:
                new_customer = StripeCustomer(
                user=user, stripe_customer_id=stripe_customer_id
                )
                new_customer.save()

                customer_id = new_customer.id

            try:
                subscription = Subscription.objects.get(customer_id=customer_id)

                if subscription is not None:
                    user.subscription = subscription
                    user.save()
            
            except Exception as _:
                return Response({"error": f"User creation failed. {_}",'checkout_session_id':checkout_session_id}, status=status.HTTP_400_BAD_REQUEST)

            send_confirmation_email(user.email, user.first_name)

            return Response({"plan": user ,'checkout_session_id':checkout_session_id}, status=status.HTTP_201_CREATED)

            
        

def getCreditsInSubscription(subscription):
    credits = subscription.items.latest().price.product.metadata['credits']
    return int(credits)




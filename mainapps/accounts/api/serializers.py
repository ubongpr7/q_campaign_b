from rest_framework import serializers,exceptions
from rest_framework.validators import UniqueValidator
from mainapps.accounts.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from mainapps.ads_manager.api.serializers import AdAccountSerializer
from mainapps.ads_manager.models import Ad
from mainapps.stripe_pay.models import Plan, Subscription, StripeCustomer
import stripe
from django.conf import settings
import uuid

from django.contrib.auth import get_user_model


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields="__all__"

class UserRegistrationSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(required=True,validators=[UniqueValidator(queryset=User.objects.all())])
    password=serializers.EmailField(required=True,validators=[UniqueValidator(queryset=User.objects.all())])
    password=serializers.CharField(required=True,write_only=True)
    class Meta:
        model=User
        fields=(
            "email",
            "username",
            "password",
            )
        
        # extra_kwargs={
        #     'password':{'write_only':True}
        # }

    def create(self, validated_data):
        user=User.objects.create(username=validated_data['username'],email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
                          

        # instance=self.Meta.model(validated_data)
        # if password is not None:
        #     instance.set_password(password)
        #     instance.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username", "")
        password = data.get("password", "")

        if username and password:
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    data["user"] = user
                else:
                    raise exceptions.ValidationError("You need to verify your account")
            else:
                raise exceptions.ValidationError("Invalid credentials")
        else:
            raise exceptions.ValidationError("All fields are required")

        return data


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['id'] = user.id
        return token 


class ProfilePictureUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['picture']

stripe.api_key=settings.STRIPE_SEC_KEY
class UserSignUpSerializer(serializers.ModelSerializer):
    sessionId = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["email", "first_name", "password", "sessionId"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        """Ensure the email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User already exists.")
        return value

    def create(self, validated_data):
        sessionId = validated_data.pop("sessionId", None)
        user = User.objects.create_user(**validated_data)
    
        if not sessionId:
            free_plan = Plan.objects.get(id=3)
            customer = stripe.Customer.create(email=user.email, name=user.first_name)
            stripe_customer = StripeCustomer.objects.create(
                user=user, stripe_customer_id=customer.id
            )
            subscription = Subscription.objects.create(
                plan=free_plan,
                credits=free_plan.vsl_limit,
                customer=stripe_customer,
                stripe_subscription_id=None,
            )
            user.subscription = subscription
            user.verification_token = str(uuid.uuid4())  
            user.save()
        else:
            checkout_session = stripe.checkout.Session.retrieve(sessionId)
            stripe_customer_id = checkout_session.customer

            customer, created = StripeCustomer.objects.get_or_create(
                stripe_customer_id=stripe_customer_id,
                defaults={"user": user}
            )

            if not created:
                customer.user = user
                customer.save()

            # Link subscription if it exists
            subscription = Subscription.objects.filter(customer=customer).first()
            if subscription:
                user.subscription = subscription
                user.save()

        return user



# class AdAccountSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Ad
#         fields = "__all__"

class ProfileSerializer(serializers.ModelSerializer):
    picture = serializers.SerializerMethodField()
    ad_accounts = AdAccountSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'picture', 'ad_accounts']

    def get_profile_picture(self, obj):
        if obj.picture:
            return obj.picture.url
        return None

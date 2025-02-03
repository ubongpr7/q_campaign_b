from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.auth import  get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Subscription, StripeCustomer, Plan
import stripe
from datetime import datetime



@csrf_exempt
def stripe_webhook(request):
  stripe.api_key = settings.STRIPE_SEC_KEY

  endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
  payload = request.body
  sig_header = request.META['HTTP_STRIPE_SIGNATURE']

  event = None
  try:
    event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
  except ValueError as _:
    return HttpResponse(status=400)
  except stripe.error.SignatureVerificationError as _:
    return HttpResponse(status=400)

  event_type = event['type']
  event_object = event['data']['object']

  if event_type == 'invoice.payment_succeeded':
    if event_object.billing_reason == 'subscription_create':
      try:
        customer_id = event_object.customer

        customer = None
        try:
          customer = StripeCustomer.objects.get(stripe_customer_id=customer_id)
        except StripeCustomer.DoesNotExist:
          customer = StripeCustomer(user=None, stripe_customer_id=customer_id)
          customer.save()

        prev_sub = None
        prev_sub_hooks = 0
        prev_sub_merges = 0
        try:
          prev_sub = Subscription.objects.get(customer_id=customer.id)

          if prev_sub is not None:
            if prev_sub.stripe_subscription_id is not None:
              stripe.Subscription.delete(prev_sub.stripe_subscription_id)

            prev_sub_hooks = prev_sub.hooks
            prev_sub_merges = prev_sub.merge_credits
        except Subscription.DoesNotExist:
          pass

        subscription_id = event_object.subscription
        price_id = event_object.lines.data[0].price.id
        plan = Plan.objects.get(stripe_price_id=price_id)
        subscription = Subscription(
          plan=plan,
          stripe_subscription_id=subscription_id,
          customer=customer,
          hooks=plan.hook_limit + prev_sub_hooks,
          merge_credits=plan.hook_limit  + prev_sub_merges
        )
        subscription.save()

        if customer.user is not None:
          customer.user.subscription = subscription
          customer.user.save()

          if prev_sub is not None:
            prev_sub.delete()
      except Exception as e:
        print(
          datetime.now().strftime("%H:%M:%S")
          + f': Error in stripe webhook: {e}'
        )
    elif event_object.billing_reason == 'subscription_cycle':
      try:
        price_id = event_object.lines.data[0].price.id
        plan = Plan.objects.get(stripe_price_id=price_id)

        subscription_id = event_object.subscription
        subscription = Subscription.objects.get(
          stripe_subscription_id=subscription_id
        )
        subscription.hooks = plan.hook_limit + subscription.hooks
        subscription.merge_credits = (
          plan.hook_limit 
        ) + subscription.merge_credits
        subscription.save()
      except Exception as e:
        print(
          datetime.now().strftime("%H:%M:%S")
          + f': Error in stripe webhook: {e}'
        )
  elif event_type == 'invoice.payment_failed':
    if event_object.billing_reason == 'subscription_create':
      messages.error(
        request,
        'Checkout error. Couldn\'t Complete Subsrciption Successfully. Please try again later.'
      )

      print(
        datetime.now().strftime("%H:%M:%S") +
        ': Payment Failed. Couldn\'t Complete Subsrciption Successfully. Please try again later.'
      )
    elif event_object.billing_reason == 'subscription_cycle':
      messages.error(
        request,
        'Checkout error. Couldn\'t Renew Subsrciption Successfully. Please try again later.'
      )

      print(
        datetime.now().strftime("%H:%M:%S") +
        ': Payment Failed. Couldn\'t Renew Subsrciption Successfully. Please try again later.'
      )
  elif event_type == 'customer.subscription.deleted':
    if event_object.cancel_at_period_end:
      customer_id = event_object.customer

      try:
        customer = StripeCustomer.objects.get(stripe_customer_id=customer_id)
      except StripeCustomer.DoesNotExist:
        return HttpResponse(status=404)

      sub = Subscription.objects.get(customer_id=customer.id)
      sub.hooks = 0
      sub.merge_credits = 0
      sub.save()
  elif event_type == 'customer.subscription.updated':
      try:
          subscription_id = event_object['id']
          price_id = event_object['items']['data'][0]['price']['id']
          plan = Plan.objects.get(stripe_price_id=price_id)

          subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)

          # Handle cancellation
          if event_object.get("canceled_at") is not None:
              subscription.plan =Plan.objects.get(id=4)
              subscription.save()
              print(f'Subscription {subscription_id} was canceled.')

          # Handle renewal or update
          # elif event_object.get("status") == "active":
          #     subscription.plan = plan
          #     # subscription.hooks += plan.hook_limit
          #     # subscription.merge_credits += plan.hook_limit
          #     subscription.save()
          #     print(f'Subscription {subscription_id} updated successfully.')

      except Subscription.DoesNotExist:
          print(f'Error: Subscription {subscription_id} not found.')
      except Exception as e:
          print(f'Error updating subscription: {e}')

  return HttpResponse(status=200)

@login_required
def manage_subscription(request):
  credits_left = request.user.subscription.hooks
  total_credits = max(request.user.subscription.plan.hook_limit, credits_left)

  current_period_end = 0
  if request.user.subscription.stripe_subscription_id is not None:
    stripe.api_key = settings.STRIPE_SEC_KEY

    subscription = stripe.Subscription.retrieve(
      request.user.subscription.stripe_subscription_id
    )

    current_period_end = int(subscription['current_period_end'])
  else:
    current_period_end = request.user.subscription.current_period_end

  now = int(datetime.now().timestamp())
  days_left = int((current_period_end-now) / 60 / 60 / 24)
  days_left = max(-1, days_left)
  days_left += 1

  return render(
    request,
    'subscription.html',
    context={
      'total_credits':
        total_credits,
      'credits_left':
        credits_left,
      'cur_plan':
        request.user.subscription.plan,
      'price_per_merge':
        f"{(2):.2f}",
      'plans':
        Plan.objects.all().order_by('id'),
      'days_left':
        days_left,
    }
  )

@login_required
def billing_portal(request):
  stripe.api_key = settings.STRIPE_SEC_KEY

  try:
    customer = StripeCustomer.objects.get(user_id=request.user.id)

    session = stripe.billing_portal.Session.create(
      customer=customer.stripe_customer_id,
      return_url=settings.DOMAIN + reverse('account:home'),
    )

    return redirect(session.url)
  except Exception as _:
    return redirect(reverse('account:home'))

def verify(request, token):
  try:
    user = get_user_model().objects.get(verification_token=token)

    if user is not None:
      user.verification_token = None
      user.save()

      _login(request, user)
      return redirect('hooks:upload')
  except:
    return redirect(reverse('account:home'))

def subscribe(request, price_id):
  if request.method == 'GET':
    try:
      stripe.api_key = settings.STRIPE_SEC_KEY

      success_path = request.GET.get('success_path')
      cancel_path = request.GET.get('cancel_path')

      customer = None
      if request.user.is_authenticated:
        customer = request.user.subscription.customer.stripe_customer_id

      checkout_session = stripe.checkout.Session.create(
        customer=customer,
        success_url=settings.DOMAIN + success_path +
        ('&' if '?' in success_path else '?')
        + 'session_id={CHECKOUT_SESSION_ID}',
        cancel_url=settings.DOMAIN + cancel_path,
        payment_method_types=['card'],
        mode='subscription',
        line_items=[{
          'price': price_id,
          'quantity': 1,
        }]
      )

      return redirect(checkout_session.url)
    except Exception as _:
      return redirect(reverse('account:home'))

@login_required
def add_credits(request, kind):
  if request.method == 'POST':
    if int(request.POST.get('credits_number')
           ) >= 1 and request.user.subscription.plan.name.lower() != 'free':
      try:
        stripe.api_key = settings.STRIPE_SEC_KEY

        unit_amount = 0
        if kind == 'hook':
          unit_amount = float(request.user.subscription.plan.price_per_hook)
        elif kind == 'merge':
          unit_amount =2
          # unit_amount = float(request.user.subscription.plan.price_per_hook / 5)

        checkout_session = stripe.checkout.Session.create(
          customer=request.user.subscription.customer.stripe_customer_id,
          success_url=settings.DOMAIN + reverse('account:add_credits_success')
          + f'?amount={request.POST.get("credits_number")}&kind={kind}',
          cancel_url=settings.DOMAIN + reverse('account:add_credits_cancel'),
          payment_method_types=['card'],
          line_items=[
            {
              'price_data':
                {
                  'currency': 'usd',
                  'product_data':
                    {
                      'name':
                        f'{request.POST.get("credits_number")} {kind.title()} Credits',
                    },
                  'unit_amount': int(round(unit_amount * 100)),
                },
              'quantity': int(request.POST.get('credits_number')),
            },
          ],
          mode='payment',
        )

        return redirect(checkout_session.url)
      except Exception as _:
        return redirect(reverse('account:home'))

@login_required
def add_credits_success(request):
  if request.method == 'GET':
    new_credits = int(request.GET.get('amount'))
    kind = request.GET.get('kind')

    if kind == 'hook':
      request.user.subscription.hooks += new_credits
    elif kind == 'merge':
      request.user.subscription.merge_credits += new_credits

    request.user.subscription.save()

    return redirect(reverse('account:manage_subscription') + '?recheck=true')

def add_credits_cancel(request):
  return redirect(reverse('account:manage_subscription'))

@login_required
def upgrade_subscription(request, price_id):
  return subscribe(request, price_id)

@login_required
def downgrade_subscription(request):
  try:
    if request.user.subscription.plan.id == 2:
      subscription = stripe.Subscription.retrieve(
        request.user.subscription.stripe_subscription_id
      )

      stripe.Subscription.modify(
        subscription.id,
        items=[
          {
            'id': subscription['items']['data'][0].id,
            'price': settings.STRIPE_PRICE_ID_PRO,
          }
        ],
        proration_behavior='none',
      )

      pro_plan = Plan.objects.get(id=1)
      request.user.subscription.plan = pro_plan
      request.user.subscription.save()

      return redirect(reverse('account:manage_subscription') + '?recheck=true')
  except Exception as e:
    return redirect(reverse('account:manage_subscription'))

@login_required
def cancel_subscription(request):
  stripe.api_key = settings.STRIPE_SEC_KEY

  try:
    subscription = stripe.Subscription.retrieve(
      request.user.subscription.stripe_subscription_id
    )
    stripe.Subscription.modify(
      subscription.id,
      cancel_at_period_end=True,
    )

    free_plan = Plan.objects.get(id=3)
    request.user.subscription.plan = free_plan
    request.user.subscription.stripe_subscription_id = None
    request.user.subscription.current_period_end = subscription.current_period_end
    request.user.subscription.save()

    return redirect(reverse('account:manage_subscription') + '?recheck=true')
  except Exception as _:
    return redirect(reverse('account:manage_subscription'))

@login_required
def subscription(request):
  sub = request.user.subscription

  return JsonResponse(
    {
      'plan_name': sub.plan.name.lower(),
      'stripe_subscription_id': sub.stripe_subscription_id,
      'hooks': sub.hooks,
      'merge_credits': sub.merge_credits,
      'current_period_end': sub.current_period_end
    }
  )


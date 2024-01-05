#webhook views.py

from django.shortcuts import render, redirect
import stripe
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User #get model User so we can insert into database
import uuid
from django.core.mail import send_mail
from django.conf import settings
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms import CodeForm
import requests
from .oauth2 import discord_oauth_callback, discord_login, discord_oauth_callback
from django.utils.html import format_html
import os
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages

#os.environ.get("STRIPE_API_KEY")

#Gets events from Stripe and checks if it is a new subscription event. If so,
# retrieves stripe info to save in db and sends user a confirmation email.
@require_POST
@csrf_exempt  # CSRF exemption for this endpoint; be cautious with this in production
def server(request):
    stripe.api_key = os.environ.get('STRIPE_API_KEY')
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('ENDPOINT_SECRET')
        )
    except ValueError as e:
        # Invalid payload
        return JsonResponse({'error': str(e)}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return JsonResponse({'error': str(e)}, status=400)
    # Handle the event
    if event['type'] == 'customer.subscription.created':
        subscription = event['data']['object']
        subscription_status = subscription['status'] 
        customer_id = subscription['customer']
        customer = stripe.Customer.retrieve(customer_id)
        #Generate unique code for user to associate stripe email with disord id
        uniqueUserCode = generate_unique_code()
        #Add User to database
        new_user = User.objects.create(stripeEmail=customer.email, userCode=uniqueUserCode, subscriptionStatus=subscription_status)
        #Send email to user with code and link
        send_email(customer.email, uniqueUserCode, os.environ.get('REDIRECT_LINK'))

    else:
        print('Unhandled event type {}'.format(event['type']))

    return JsonResponse({'success': True})

#Gets unique code from User input and saves in session to be used later
def login(request):
    if request.method == 'POST':
        form = CodeForm(request.POST)
        if form.is_valid():
            user_code = form.cleaned_data['code']
            if User.objects.filter(userCode = user_code).exists():
                request.session['user_code'] = user_code
                # Proceed with Discord OAuth
                # Redirect to Discord OAuth process -> in urls.py -> 
                # path('discord/oath/callback/', views.oAuth2, name='discord_authorization')
                return redirect('discord_authorization')  
    else:
        messages.error(request, "Code not found. Please try again.")

    return render(request, 'login.html', {'form': form})
   


#OAuth2 functionality for Discord, return discord_login() function from Oauth2.py
def oAuth2(request):

    return discord_login() 

#OAuth2 redirect for Discord, returns discord_oauth_callback function from Oauth2.py
def oauthRedirect(request):

   return discord_oauth_callback(request)

#Fetches member joined event from bot server and calls back to bot server to assign user 'Gold Role'
@require_POST
@csrf_exempt  
def member_joined_notification(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    member_id = data.get('member_id')
    if member_id is None:
        return JsonResponse({'error': 'member_id is required'}, status=400)

    # Process the new member data here
    if checkActiveSubscription(member_id):
        print("User has active subscription")
        url = os.environ.get('ASSIGN_ROLE_URL')
        data = {'discord_id': member_id}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            # Handle success
            return JsonResponse({'status': 'success', 'data': response.json()})
        else:
            # Handle failure
            return JsonResponse({'status': 'error', 'message': 'Failed to assign role'}, status=500)
    except requests.RequestException as e:
        # Handle request exception
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
##### Helper Functions #####

#Checks for Discord Id and subscription status = 'active' in database
def checkActiveSubscription(user_id):
    try:
        return User.objects.filter(discordID=user_id, subscriptionStatus="active").exists() 
    except User.DoesNotExist:
        return False

#Generates unique code using uuid
def generate_unique_code():
    while True:
        userCode = str(uuid.uuid4())  # Generate a random UUID
        if not User.objects.filter(userCode=userCode).exists():
            return userCode

#Sends email 
def send_email(email, code, link):
    html_content = render_to_string('email.html', {'access_code': code,'link': link})
    text_content = strip_tags(html_content)
    
    send_mail(
        'Claim Discord Access', # Subject
        text_content,   # Message
        settings.EMAIL_HOST_USER, # From email
        [email],  # To email (list)
        html_message=html_content,
        fail_silently=False,
    )
        



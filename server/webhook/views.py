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


#test locally with command line
#will need to add endpoint to live url
@require_POST
@csrf_exempt  # CSRF exemption for this endpoint; be cautious with this in production
def server(request):
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
    if event['type'] == 'payment_intent.succeeded':
        #payment_intent = event['data']['object']
        print('payment succeeded')
        stripeEmail = 'ijwolf8@gmail.com'
        #MAKE SURE GENERATED CODE IS UNIQUE (IF-ELSE)
        uniqueUserCode = generate_unique_code()
        # add User to DB
        new_user = User.objects.create(stripeEmail=stripeEmail, userCode=uniqueUserCode)
        # Send email to user with code and link
        #send_email(stripeEmail, uniqueUserCode, redirect_link)

    else:
        print('Unhandled event type {}'.format(event['type']))

    return JsonResponse({'success': True})


def login(request): #need to handle request from user
    #User enters code
    #store code in variable
    # call discord OAUTH2 function
    #get email from OAUTH2 and search up code in User db
    #assign email to User with the code
    if request.method == 'POST':
        form = CodeForm(request.POST)
        if form.is_valid():
            request.session['user_code'] = form.cleaned_data['code']
            # Now that you have the code, proceed with Discord OAuth
            return redirect('discord_authorization')  # Redirect to Discord OAuth process
    else:
        form = CodeForm()

    return render(request, 'login.html', {'form': form})
    print('Discord OAUTH2')
    return 'Discord OAUTH2'

#OAuth2 functionality for Discord
def oAuth2(request):
    #call oauth2.py
    #get email and access token
    #add email to database by looking up user code from login
    #what to do with access token?

    return discord_login() #pass request here?

def oauthRedirect(request):

   return discord_oauth_callback(request)


@require_POST
@csrf_exempt  # CSRF exemption for this endpoint; be cautious with this in production
def member_joined_notification(request):
    data = json.loads(request.body)
    member_id = data.get('member_id')
    member_name = data.get('member_name')

    # Process the new member data here
    if checkActiveSubscription(member_id):
        url = 'http://127.0.0.1:5001/assignRole'  # URL of the bot server
        data = {'discord_id': member_id}
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("Role assignment request sent successfully")
        else:
            print("Failed to send role assignment request")
                

    return JsonResponse({'status': 'Received'})


def checkActiveSubscription(user_id):
    try:
        # Assuming 'active' is the value representing an active status
        return User.objects.filter(discordID=user_id).exists()
        #subscriptionStatus=None
    except User.DoesNotExist:
        return False


def generate_unique_code():
    while True:
        userCode = str(uuid.uuid4())  # Generate a random UUID
        if not User.objects.filter(userCode=userCode).exists():
            return userCode

def send_email(email, code, link):
    clickableLink = format_html("Click on this link <a href='{}'>link</a> and enter your confirmation code. Here is your confirmation code:  ", link)
        
    send_mail(
        'Confirmation',                 # Subject
        clickableLink + code ,         # Message
        settings.EMAIL_HOST_USER,       # From email
        [email],             # To email (list)
        fail_silently=False,
    )


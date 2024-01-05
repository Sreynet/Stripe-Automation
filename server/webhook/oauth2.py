# views.py
from django.conf import settings
from django.shortcuts import redirect
import requests
from django.http import JsonResponse
from django.shortcuts import render
from .models import User
import sys
from pathlib import Path
import os
from django.core.mail import send_mail

# ... other imports ...
client_id = os.environ.get('CLIENT_ID')
redirect_uri = os.environ.get('REDIRECT_URI')
client_secret = os.environ.get('CLIENT_SECRET')
invite_link = os.environ.get('DISCORD_INVITE_LINK')

#Redirect to discord login link for authorization with discord scope to identify discord user
def discord_login():
    discord_oauth_url = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=identify"
    return redirect(discord_oauth_url) 


#Redirection from discord_login()                                                       
def discord_oauth_callback(request):
    code = request.GET.get('code')
    if code:
        #Exchange the authorization code for an access token
        token_url = 'https://discord.com/api/oauth2/token'
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'scope': 'identify',
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Exchange code for token
        response = requests.post(token_url, data=data, headers=headers)
        token_data = response.json()
        access_token = token_data['access_token']

        #Use the access token to get user information
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            user_response = requests.get('https://discord.com/api/v6/users/@me', headers={'Authorization': f'Bearer {access_token}'})
            #Checks if authorization is successful
            if user_response.status_code == 200:
                #Get user's id from Discord
                user_id = user_response.json().get('id')
                #Get user code from request session
                user_code = request.session.get('user_code') 
                #Check ti see if user code is in database, if it is not USER NEEDS TO BE PROMPTED TO REENTER
                if User.objects.filter(userCode = user_code).exists():
                    #items = Item.objects.filter(column1='value1', column2='value2')
                    user = User.objects.get(userCode = user_code)
                    userStripeEmail = user.stripeEmail
                    user.discordID = user_id
                    user.save()
                    del request.session['user_code']
                    #Send invite link to User just in case they lose it
                    send_mail(
                        'Discord Invite',                            #Subject
                        "Here is your invite link" + invite_link ,   #Message
                        settings.EMAIL_HOST_USER,                    #From email
                        [userStripeEmail],                           #To email (list)
                        fail_silently=False,
    )               #redirect invite link to discord server
                    return redirect(invite_link)
                return  
    
    return render(request, 'error.html')



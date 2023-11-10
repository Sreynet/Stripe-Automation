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
# Get the directory of the current file
#current_file = Path(__file__).resolve()

# Get the parent directory
#parent_dir = current_file.parent

# Add the parent directory to sys.path
#if str(parent_dir) not in sys.path:
    #sys.path.append(str(parent_dir))

# ... other imports ...
client_id = os.environ.get('CLIENT_ID')
redirect_uri = os.environ.get('REDIRECT_URI')
client_secret = os.environ.get('CLIENT_SECRET')

def discord_login():
    discord_oauth_url = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=identify"
    return redirect(discord_oauth_url) #will this throw an error bc it is not in urls.py and is returning a url

#go to auth link
#after auth link redirect                                                       
def discord_oauth_callback(request):
    code = request.GET.get('code')
    if code:
        # Step 3: Exchange the authorization code for an access token
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

        # Step 4: Use the access token to get user information
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            user_response = requests.get('https://discord.com/api/v6/users/@me', headers={'Authorization': f'Bearer {access_token}'})
            
            if user_response.status_code == 200:
                user_id = user_response.json().get('id')
                # Now you have the user's email from Discord
                # You can proceed with your logic here
                #add user id to database by looking for matching code
                user_code = request.session.get('user_code') #NEED TO CHECK THAT CODE THAT USER ENTERED IS THE SAME AS IN THE EMAIL, IF NOT TELL USER TO REENTER. DONE BY CHECKING IF IN DB
                if User.objects.filter(userCode = user_code).exists():
                    user = User.objects.get(userCode = user_code)
                    user.discordID = user_id
                    user.save()
                    del request.session['user_code']
                    #redirect to link
                    invite_link = "https://discord.gg/CkNWhq52" #NEED TO PUT IN .ENV 
                    return redirect(invite_link)
                    #if checkActiveSubscription(user_id):
                        #url = 'http://localhost:5001/assign_role'  # URL of the Flask server
                        #data = {'discord_id': discord_id}
                        #response = requests.post(url, json=data)
                        #if response.status_code == 200:
                            #print("Role assignment request sent successfully")
                        #else:
                            #print("Failed to send role assignment request")
                #EMAIL INVITE LINK TOOOOOOOOOOO
                return redirect("https://discord.gg/CkNWhq52")  #NEED TO PUT IN .ENV #OPENS DISCORD APP FOR USER TO ACCEPT INVITE, IN BROWSER IF USER LOGGED IN DOES NOT REDIRECT USER TO INVITE LINK. USER ONLY REDIRECTED CORRECTLY IF DISCORD IS OPENED
                #return render(request, 'success.html', {'user_id': user_id})
    
    return render(request, 'error.html')


'''   # This view handles the callback from Discord OAuth
    # You would typically exchange the code for a token and then use the token to get user data

    discord_code = request.GET.get('code')
    if discord_code:
        token_data = {
            'client_id': settings.DISCORD_CLIENT_ID,
            'client_secret': settings.DISCORD_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': discord_code,
            'redirect_uri': 'http://localhost:8000/discord/oauth/callback/',
            'scope': 'identify email'
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        token_response = requests.post('https://discord.com/api/oauth2/token', data=token_data, headers=headers)

        if token_response.status_code == 200:
            access_token = token_response.json().get('access_token')
            user_response = requests.get('https://discord.com/api/v6/users/@me', headers={'Authorization': f'Bearer {access_token}'})
            
            if user_response.status_code == 200:
                user_email = user_response.json().get('email')
                # Now you have the user's email from Discord
                # You can proceed with your logic here
                return render(request, 'success.html', {'email': user_email})
    
    return render(request, 'error.html')
'''
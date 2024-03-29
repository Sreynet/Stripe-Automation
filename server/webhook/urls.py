from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.server, name='webhook'),
    path('login/', views.login, name='login'),
    path('discord/oath/callback/', views.oAuth2, name='discord_authorization'),
    path ('oAuthDiscord/oauth/' , views.oauthRedirect,name='oauth_redirect'),
    path ('join/' , views.member_joined_notification,name='member_join')
]

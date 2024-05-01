from django.shortcuts import render
from django.shortcuts import redirect
from accounts.models import CustomUser
import secrets
import string
import requests
from urllib.parse import urlencode
from pathlib import Path
import environ
import os
import time

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Initialise environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Client info
CLIENT_ID = env('CLIENT_ID')
CLIENT_SECRET = env('CLIENT_SECRET')
REDIRECT_URI = env('REDIRECT_URI')


# Spotify API endpoints
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
ME_URL = 'https://api.spotify.com/v1/me'

# Request authorization from user
scope = 'user-modify-playback-state user-read-currently-playing'

def authorizecode(id, code):
    # Request tokens with code we obtained
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }
    print(f"*****************************{payload}")
    res = requests.post(TOKEN_URL, auth=(CLIENT_ID, CLIENT_SECRET), data=payload)
    res_data = res.json()
    print(f"*****res_data***{res_data}")
    
    user = CustomUser.objects.get(id=id)
    user.refresh_token = res_data.get('refresh_token')
    user.access_token = res_data.get('access_token')
    user.boycott_active = True
    user.save()    

    return "Credentials stored successfully"

def refresh(id, refresh_token):
    '''Refresh access token.'''
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    res = requests.post(
        TOKEN_URL, auth=(CLIENT_ID, CLIENT_SECRET), data=payload, headers=headers
    )
    res_data = res.json()
    
    user = CustomUser.objects.get(id=id)
    user.access_token = res_data.get('access_token')
    user.boycott_active = True
    user.save()  

    return res_data

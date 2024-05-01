from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from accounts.models import CustomUser
from urllib.parse import urlencode
from . import spotify
import requests
import time
import secrets
import json
import string

@api_view(['POST'])
def login_view(request):
    # data = json.loads(request.data)
    data = request.data
    username = data.get('username')
    password = data.get('password')
    if username is None or password is None:
        return JsonResponse({'detail': 'Please provide username and password.'}, status=400)

    user = authenticate(username=username, password=password)

    if user is None:
        return JsonResponse({'detail': 'Invalid credentials.'}, status=400)

    login(request, user)
    return JsonResponse({'detail': 'Successfully logged in.'})


def logout_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'You\'re not logged in.'}, status=400)

    logout(request)
    return JsonResponse({'detail': 'Successfully logged out.'})


@ensure_csrf_cookie
def session_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False})

    return JsonResponse({'isAuthenticated': True})


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def artists(request):
    ''' Handles the artist portion of this service.'''
    user = CustomUser.objects.get(id=request.user.id)
    artists = user.bad_artists
    if request.method == 'POST':
        if request.data.get('append'):
            artists.append(request.data.get('append'))
        elif request.data.get('remove'):
            artists.remove(request.data.get('remove'))
        user.bad_artists = artists
        user.save() 
        user = CustomUser.objects.get(id=request.user.id)
        artists = user.bad_artists
        return  Response({
            'user': user.id,
            'artists': artists
        })
    return Response({
        'user': request.user.id,
        'method': request.method,
        'is authed': request.user.is_authenticated,
        'artists': artists
        })


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def boycott(request):
    ''' Handles enabling portion of this service.'''
    user = CustomUser.objects.get(id=request.user.id)
    boycott = user.boycott_active
    if request.method == 'POST':
        print(request.data)
        user.boycott_active = request.data.get('boycott')
        user.save() 
        user = CustomUser.objects.get(id=request.user.id)
        boycott = user.boycott_active
        return  Response({
            'user': user.id,
            'boycott': boycott
        })
    return Response({
        'user': request.user.id,
        'boycott': boycott
        })

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def spotifyAuth(request):
    # redirect_uri can be guessed, so let's generate
    # a random `state` string to prevent csrf forgery.
    state = ''.join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16)
    )
    payload = {
            'client_id': spotify.CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': spotify.REDIRECT_URI,
            'state': state,
            'scope': spotify.scope
        }
    url = f'{spotify.AUTH_URL}/?{urlencode(payload)}'
    # frontend will need to redirect to this url
    return Response({
        'response': url
    })


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def callback(request):
    #this part sends the callback code to the server and then completes the rest of the spotify auth. returns an OK msg, then react redirects to /me
    res = spotify.authorizecode(id=request.user.id, code=request.data.get('code'))
    # return redirect('/')
    return  Response({
            'data': res
        })


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def me(request):
    user = CustomUser.objects.get(id=request.user.id)
    if (user.refresh_token):
        tokens = {
            'access_token': user.access_token,
            'refresh_token': user.refresh_token
        }
        # Get profile info
        headers = {'Authorization': f"Bearer {tokens.get('access_token')}"}
        response = requests.get(spotify.ME_URL, headers=headers)
        while response.status_code != 200:
            headers = {'Authorization': f"Bearer {tokens.get('access_token')}"}
            response = requests.get(spotify.ME_URL, headers=headers)
            match response.status_code:
                case 200:
                    pass
                case 401:
                    # do refresh actions here
                    tokens = spotify.refresh(id=user.id, refresh_token=tokens.get('refresh_token'))
                case 429:
                    print("****************************************RATELIMIT")
                    time.sleep(1)
                case _:
                    print(f"****************************************{response.status_code} error, unable to proceed")
        res_data = response.json()
        return Response({ 
            'data': res_data, 
            'artists': user.bad_artists 
            })
    else:
        return Response({
        'error': 404
        })
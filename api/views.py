from django.core.mail import send_mail
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from accounts.models import CustomUser
from urllib.parse import urlencode
from . import spotify
import requests
import time
import secrets
import string

@api_view(['POST'])
def signup_view(request):
    data = request.data
    password = data.get('password')
    email = data.get('email').lower()

    try:
        validate_email(email)
    except ValidationError as error:
        return Response({'message': error}, status=400)
    
    if len(password) < 8:
        return Response({'message': 'Password must be at least 8 characters.'}, status=400)
    
    try:
        user = CustomUser.objects.create_user( email=email, password=password)
    except Exception as error:
        return Response({'message': f"Error creating user: {error}"}, status=400)

    login(request, user)
    send_mail(
        subject='Welcome to Skipify!', 
        message="Thank you for signing up! We are excited to have you on board.\n"
        "Please let us know if you have any questions or feedback.\n\n"
        f"Username: {email}\n"
        "Best,\nThe Skipify Team",
        from_email='bot@thinkmartell.com',
        recipient_list=[email], 
        fail_silently=False
        )
    return Response({'message': 'Successfully logged in.'})


@api_view(['POST'])
def login_view(request):
    data = request.data
    email = data.get('email')
    password = data.get('password')
        
    try:
        user = authenticate(username=email, password=password)
    except Exception as error:
        return Response({'message': error}, status=400)

    if user is None:
        return Response({'message': 'Invalid credentials.'}, status=400)

    login(request, user)
    return Response({'message': 'Successfully logged in.'})

@api_view(['GET'])
def logout_view(request):
    if not request.user.is_authenticated:
        return Response({'message': 'You\'re not logged in.'}, status=400)

    logout(request)
    return Response({'message': 'Successfully logged out.'})

@api_view(['GET'])
@ensure_csrf_cookie
def session_view(request):
    if not request.user.is_authenticated:
        return Response({'isAuthenticated': False}, content_type='application/json')

    return Response({'isAuthenticated': True}, content_type='application/json')


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

# @api_view(['GET'])
# @authentication_classes([SessionAuthentication])
# @permission_classes([IsAuthenticated])
# def spotifyAuth(request):
#     # redirect_uri can be guessed, so let's generate
#     # a random `state` string to prevent csrf forgery.
#     state = ''.join(
#         secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16)
#     )
#     payload = {
#             'client_id': spotify.CLIENT_ID,
#             'response_type': 'code',
#             'redirect_uri': spotify.REDIRECT_URI,
#             'state': state,
#             'scope': spotify.scope
#         }
#     url = f'{spotify.AUTH_URL}/?{urlencode(payload)}'
#     # frontend will need to redirect to this url
#     return Response({
#         'response': url
#     })


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
        tokens = spotify.refresh(id=user.id, refresh_token=user.refresh_token)
        return Response({ 
            'data': tokens.access_token,
            })
    else:
        return Response({
        'error': 404,
        'data': 'No refresh token found. Unable to provide access token.'
        })

# I want to sort this to disable cors here or maybe i should just disable cors for the whole thing.  
# @api_view(['GET'])
# def deployment(request):
#     return Response({
#         'data': 'old message here'
#     })
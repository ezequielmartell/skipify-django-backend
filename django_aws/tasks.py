import logging
import time

from django_aws import celery
from accounts.models import CustomUser
import time
from pathlib import Path
import environ
import os
import requests


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Initialise environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# app = Celery("django_aws")

# Client info
CLIENT_ID = env('CLIENT_ID')
CLIENT_SECRET = env('CLIENT_SECRET')
REDIRECT_URI = env('REDIRECT_URI')

TOKEN_URL = 'https://accounts.spotify.com/api/token'
PLAYER_URL = 'https://api.spotify.com/v1/me/player'


@celery.app.task()
def sync_boycott_tasks():
    users = CustomUser.objects.all()
    for user in users:
        if user.boycott_active:
            minute_skipping_task.delay(user.id)


@celery.app.task()
def minute_skipping_task(user_id):
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
        user.save()  

        return res_data
    
    def skip_track(tokens):
        print(f"User: {user.id} - skipping track!")
        headers = {
    "Authorization": f"Bearer {tokens['access_token']}"
}
        response = requests.post(f"{PLAYER_URL}/next", headers=headers)

    user = CustomUser.objects.get(id=user_id)
    tokens = {
        'access_token': user.access_token,
        'refresh_token': user.refresh_token
    }
    time_end = time.time() + 60 * 1
    while time.time() < time_end:
        headers = {
    "Authorization": f"Bearer {tokens['access_token']}"
}
        response = requests.get(PLAYER_URL, headers=headers)
        match response.status_code:
        # match 429:
            case 200:
                currentSong = response.json()
                # print(f"User: {user.id} - {currentSong.get('item').get('name')})
                current_artists = [artist.get('name') for artist in currentSong.get('item').get('artists')]
                # print(f"User: {user.id} - current artists: {current_artists}")
                # print(f"User: {user.id} - user boycott artists: {user.bad_artists}")
                artist_test = any(artist in user.bad_artists for artist in current_artists)
                # print(f"User: {user.id} - Boycotting one of {current_artists}? {artist_test}")
                if artist_test:
                    skip_track(tokens=tokens)
                    print(f"User: {user.id} - Boycotting one of {current_artists}")
                time.sleep(3)
            case 204:
                # print(f"User: {user.id} - No Content to Display")
                time.sleep(10)
            case 401:
                # do refresh actions here
                # print(f"User: {user.id} - refreshing token")
                tokens = refresh(id=user_id, refresh_token=tokens.get('refresh_token'))
            case 429:
                print(f"User: {user.id} - RATELIMIT")
                time.sleep(1)
            case _:
                print(f"User: {user.id} - {response.status_code} error, unable to proceed")


@celery.app.task()
def web_task() -> None:
    logging.info("Starting web task...")
    time.sleep(10)
    logging.info("Done web task.")

@celery.app.task()
def beat_task() -> None:
    logging.info("Starting beat task...")
    time.sleep(10)
    logging.info("Done beat task.")

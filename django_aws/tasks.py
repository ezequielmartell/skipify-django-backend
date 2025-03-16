import logging
import time
from django_aws import celery
from accounts.models import CustomUser, TaskLock
from django.db import transaction
from django.utils.timezone import now, timedelta
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


@celery.app.task(bind=True)
def sync_boycott_tasks(self):
    lock_task_name = "sync_boycott_tasks"
    try:
        with transaction.atomic():
            lock, created = TaskLock.objects.get_or_create(task_name=lock_task_name)
            if lock.is_locked:
                logging.info(f"{lock_task_name} is already running, requeuing.")
                self.apply_async(countdown=3)  # Requeue in 3 seconds
                return
            logging.info(f"Acquiring lock for {lock_task_name}")
            lock.is_locked = True
            lock.save()

        users = CustomUser.objects.filter(boycott_active=True).values_list('id', flat=True)
        logging.info(f"Starting boycott tasks for users: {users}")
        [minute_skipping_task.delay(user_id) for user_id in users]

    finally:
        # Release the lock after completion or failure
        logging.info(f"Releasing lock for {lock_task_name}")
        TaskLock.objects.filter(task_name=lock_task_name).update(is_locked=False)


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
        logging.info(f"User: {user.id} - skipping track!")
        headers = {
    "Authorization": f"Bearer {tokens['access_token']}"
}
        response = requests.post(f"{PLAYER_URL}/next", headers=headers)

    user = CustomUser.objects.get(id=user_id)
    tokens = {
        'access_token': user.access_token,
        'refresh_token': user.refresh_token
    }
    time_end = time.time() + 15
    while time.time() < time_end:
        headers = {
    "Authorization": f"Bearer {tokens['access_token']}"
}
        response = requests.get(PLAYER_URL, headers=headers)
        match response.status_code:
        # match 429:
            case 200:
                currentSong = response.json()
                current_artists = [artist.get('name') for artist in currentSong.get('item').get('artists')]
                artist_test = any(artist in user.bad_artists for artist in current_artists)
                # logging.info(f"User: {user.id} - Boycotting one of {current_artists}? {artist_test}")
                if artist_test:
                    skip_track(tokens=tokens)
                    logging.info(f"User: {user.id} - Boycotting one of {current_artists}")
                time.sleep(3)
            case 204:
                logging.debug(f"User: {user.id} - No Content to Display")
                time.sleep(10)
            case 401:
                # do refresh actions here
                logging.info(f"User: {user.id} - refreshing token")
                tokens = refresh(id=user_id, refresh_token=tokens.get('refresh_token'))
            case 429:
                logging.info(f"User: {user.id} - RATELIMIT")
                time.sleep(1)
            case _:
                logging.info(f"User: {user.id} - {response.status_code} error, unable to proceed -- {response.content}")
                time.sleep(10)

@celery.app.task()
def beat_test():
    logging.info("Beat test task running")
    time.sleep(5)
    logging.info("Beat test task finished")
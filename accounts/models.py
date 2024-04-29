from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # code_challenge = models.CharField(max_length=128)
    refresh_token = models.CharField(max_length=500, blank=True)
    access_token = models.CharField(max_length=500, blank=True)
    bad_artists = models.JSONField(blank=True, default=list)
    boycott_active = models.BooleanField(default=False)
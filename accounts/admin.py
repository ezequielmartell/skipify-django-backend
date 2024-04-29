from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

fields = list(UserAdmin.fieldsets)
fields.append(("Custom Data", {'fields': ('refresh_token', 'access_token', 'bad_artists', 'boycott_active')}))
UserAdmin.fieldsets = tuple(fields)

admin.site.register(CustomUser, UserAdmin)
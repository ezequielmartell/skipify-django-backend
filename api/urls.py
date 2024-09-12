from django.urls import path
from . import views

urlpatterns = [
    path('artists/', views.artists, name="artists"),
    path('callback/', views.callback, name="callback"),
    # path('spotifyAuth/', views.spotifyAuth, name="spotifyAuth"),
    path('boycott/', views.boycott, name='boycott'),
    path('me/', views.me, name="me"),
    path('login/', views.login_view, name='api-login'),
    path('logout/', views.logout_view, name='api-logout'),
    path('signup/', views.signup_view, name='api-signup'),
    path('session/', views.session_view, name='api-session'),
]

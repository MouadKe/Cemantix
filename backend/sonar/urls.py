# sonar/api/urls.py
# Mount these under /games/ in your root urls.py:
#
#   from sonar.api.urls import urlpatterns as game_urls
#   path("games/", include((game_urls, "sonar"))),

from django.urls import path
from .views import (
    CreateRoomView,
    JoinRoomView,
    RoomStateView,
    RoomSettingsView,
    StartGameView,
    GuessView,
)

urlpatterns = [
    # POST   /games/                    → create room
    path("", CreateRoomView.as_view(), name="create-room"),

    # POST   /games/<room_id>/join/     → join room
    path("<str:room_id>/join/", JoinRoomView.as_view(), name="join-room"),

    # GET    /games/<room_id>/          → poll room state
    path("<str:room_id>/", RoomStateView.as_view(), name="room-state"),

    # PATCH  /games/<room_id>/settings/ → edit settings (creator only)
    path("<str:room_id>/settings/", RoomSettingsView.as_view(), name="room-settings"),

    # POST   /games/<room_id>/start/    → start game (creator only)
    path("<str:room_id>/start/", StartGameView.as_view(), name="start-game"),

    # POST   /games/<room_id>/guess/    → submit a guess
    path("<str:room_id>/guess/", GuessView.as_view(), name="guess"),
]
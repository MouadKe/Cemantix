# sonar/api/permissions.py

from rest_framework.permissions import BasePermission, IsAuthenticated
from .models.registry import get_room


class IsRoomPlayer(BasePermission):
    """
    Allows access only to users who have already joined the room
    identified by the `room_id` URL kwarg.
    """
    message = "You are not a player in this room."

    def has_permission(self, request, view):
        if not request.user or request.user.is_anonymous:
            return False
        room_id = view.kwargs.get("room_id")
        room = get_room(room_id)
        if room is None:
            # Let the view return a proper 404
            return True
        return room.has_player(request.user.username)


class IsRoomCreator(BasePermission):
    """
    Allows access only to the creator of the room.
    Must be combined with IsAuthenticated.
    """
    message = "Only the room creator can perform this action."

    def has_permission(self, request, view):
        if not request.user or request.user.is_anonymous:
            return False
        room_id = view.kwargs.get("room_id")
        room = get_room(room_id)
        if room is None:
            return True  # Let the view return a 404
        return room.creator_username == request.user.username
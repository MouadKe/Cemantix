from django.shortcuts import render

# Create your views here.


# sonar/api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models.registry import create_room, get_room
from .models.registry import MAX_PLAYERS
from .serializers import (
    SettingsSerializer,
    GuessSerializer,
    RoomStateSerializer,
    GuessResultSerializer,
    CreateRoomSerializer,
)
from .permissions import IsRoomCreator, IsRoomPlayer


def _get_room_or_404(room_id: str):
    """Helper: return room or raise a 404-style Response."""
    room = get_room(room_id)
    if room is None:
        return None, Response(
            {"detail": f"Room '{room_id}' not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    return room, None


# ---------------------------------------------------------------------------
# POST /games/
# ---------------------------------------------------------------------------

class CreateRoomView(APIView):
    """
    Create a new Sonar game room.
    The authenticated user becomes the creator and is automatically joined.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        room = create_room(request.user.username)
        serializer = CreateRoomSerializer({
            "room_id": room.room_id,
            "status": room.status,
            "creator": room.creator_username,
        })
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# POST /games/{room_id}/join/
# ---------------------------------------------------------------------------

class JoinRoomView(APIView):
    """
    Join an existing room.
    Fails if the room is full or the game has already started.
    Idempotent: joining a room you are already in returns 200.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        room, err = _get_room_or_404(room_id)
        if err:
            return err

        username = request.user.username

        # Idempotent: already a member
        if room.has_player(username):
            return Response(room.to_dict(), status=status.HTTP_200_OK)

        if room.status != "waiting":
            return Response(
                {"detail": "Cannot join a game that has already started."},
                status=status.HTTP_409_CONFLICT,
            )

        if room.is_full():
            return Response(
                {"detail": f"Room is full (max {MAX_PLAYERS} players + bots)."},
                status=status.HTTP_409_CONFLICT,
            )

        room.add_player(username)
        return Response(room.to_dict(), status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# GET /games/{room_id}/
# ---------------------------------------------------------------------------

class RoomStateView(APIView):
    """
    Polling endpoint. Returns the full current state of the room.
    Clients should call this every N seconds to detect state changes.
    """
    permission_classes = [IsAuthenticated, IsRoomPlayer]

    def get(self, request, room_id):
        room, err = _get_room_or_404(room_id)
        if err:
            return err

        serializer = RoomStateSerializer(room.to_dict())
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# PATCH /games/{room_id}/settings/
# ---------------------------------------------------------------------------

class RoomSettingsView(APIView):
    """
    Edit game settings. Creator only, pre-start only.
    Accepts a partial payload — only send what you want to change.
    """
    permission_classes = [IsAuthenticated, IsRoomCreator]

    def patch(self, request, room_id):
        room, err = _get_room_or_404(room_id)
        if err:
            return err

        if room.status != "waiting":
            return Response(
                {"detail": "Cannot edit settings after the game has started."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = SettingsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Apply only the fields that were provided
        if "language" in data:
            room.game.set_language(data["language"])
        if "word_pack" in data:
            room.game.set_word_pack(data["word_pack"])
        if "bots" in data:
            # Validate total capacity before applying
            human_count = len(room.player_usernames)
            if human_count + len(data["bots"]) > MAX_PLAYERS:
                return Response(
                    {"detail": f"Total players + bots cannot exceed {MAX_PLAYERS}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            room.game.set_bots(data["bots"])

        return Response(room.to_dict(), status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# POST /games/{room_id}/start/
# ---------------------------------------------------------------------------

class StartGameView(APIView):
    """
    Start the game. Creator only.
    After this point settings can no longer be edited and no new players can join.
    """
    permission_classes = [IsAuthenticated, IsRoomCreator]

    def post(self, request, room_id):
        room, err = _get_room_or_404(room_id)
        if err:
            return err

        if room.status != "waiting":
            return Response(
                {"detail": "Game has already started."},
                status=status.HTTP_409_CONFLICT,
            )

        room.status = "started"
        room.game.start(room.player_usernames)

        return Response(room.to_dict(), status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# POST /games/{room_id}/guess/
# ---------------------------------------------------------------------------

class GuessView(APIView):
    """
    Submit a word guess.
    Returns the score for this guess and whether the game is now over.
    All players in the room see the updated state on their next poll.
    """
    permission_classes = [IsAuthenticated, IsRoomPlayer]

    def post(self, request, room_id):
        room, err = _get_room_or_404(room_id)
        if err:
            return err

        if room.status != "started":
            return Response(
                {"detail": "The game is not currently in progress."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = GuessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        guess = serializer.validated_data["guess"]

        username = request.user.username
        score_result = room.game.submit_guess(username, guess)
        game_continues = room.game.advance_turn()

        if not game_continues:
            room.status = "finished"

        response_data = {
            "username": username,
            "word_score": score_result["word_score"],
            "total_score": score_result["total_score"],
            "game_over": not game_continues,
            "final_scores": room.game.get_scores() if not game_continues else None,
        }

        result_serializer = GuessResultSerializer(response_data)
        return Response(result_serializer.data, status=status.HTTP_200_OK)
# sonar/api/serializers.py

from rest_framework import serializers

VALID_LANGUAGES = ["english", "french", "arabic"]
VALID_BOT_LEVELS = ["noob", "pro", "hacker"]
VALID_WORD_PACKS = ["science", "history", "sports", "general", "default"]


# ---------------------------------------------------------------------------
# Inbound serializers (validate request data)
# ---------------------------------------------------------------------------

class SettingsSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=VALID_LANGUAGES, required=False)
    word_pack = serializers.ChoiceField(choices=VALID_WORD_PACKS, required=False)
    bots = serializers.ListField(
        child=serializers.ChoiceField(choices=VALID_BOT_LEVELS),
        max_length=3,
        required=False,
    )

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("At least one setting must be provided.")
        return attrs


class GuessSerializer(serializers.Serializer):
    guess = serializers.CharField(max_length=100, trim_whitespace=True)

    def validate_guess(self, value):
        if not value:
            raise serializers.ValidationError("Guess cannot be empty.")
        return value.lower()


# ---------------------------------------------------------------------------
# Outbound serializers (shape response data)
# ---------------------------------------------------------------------------

class SettingsResponseSerializer(serializers.Serializer):
    language = serializers.CharField()
    word_pack = serializers.CharField()
    bots = serializers.ListField(child=serializers.CharField())


class RoomStateSerializer(serializers.Serializer):
    """Used by the polling GET endpoint."""
    room_id = serializers.CharField()
    status = serializers.CharField()
    creator = serializers.CharField()
    players = serializers.ListField(child=serializers.CharField())
    current_turn = serializers.CharField(allow_null=True)
    scores = serializers.DictField(child=serializers.IntegerField())
    settings = SettingsResponseSerializer()


class GuessResultSerializer(serializers.Serializer):
    username = serializers.CharField()
    word_score = serializers.IntegerField()
    total_score = serializers.IntegerField()
    game_over = serializers.BooleanField()
    # Populated only when game_over=True
    final_scores = serializers.DictField(
        child=serializers.IntegerField(),
        required=False,
        allow_null=True,
    )


class CreateRoomSerializer(serializers.Serializer):
    """Response when a room is created."""
    room_id = serializers.CharField()
    status = serializers.CharField()
    creator = serializers.CharField()
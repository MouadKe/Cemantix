# sonar/models/registry.py
# In-memory registry mapping room_id -> RoomState.
# For production, swap this for a Redis-backed store.

import uuid
from dataclasses import dataclass, field
from typing import Optional

from .game import SonarGame

MAX_PLAYERS = 4  # human slots + bot slots combined


@dataclass
class RoomState:
    room_id: str
    creator_username: str
    game: SonarGame
    player_usernames: list[str] = field(default_factory=list)
    status: str = "waiting"  # "waiting" | "started" | "finished"

    def is_full(self) -> bool:
        return (len(self.player_usernames) + len(self.game.bots)) >= MAX_PLAYERS

    def has_player(self, username: str) -> bool:
        return username in self.player_usernames

    def add_player(self, username: str) -> None:
        if username not in self.player_usernames:
            self.player_usernames.append(username)

    def to_dict(self) -> dict:
        """Serialise room state for the polling endpoint."""
        return {
            "room_id": self.room_id,
            "status": self.status,
            "creator": self.creator_username,
            "players": list(self.player_usernames),
            "current_turn": self.game.get_current_turn(),
            "scores": self.game.get_scores(),
            "settings": {
                "language": self.game.language,
                "word_pack": self.game.word_pack,
                "bots": list(self.game.bots),
            },
        }


# ---------------------------------------------------------------------------
# Module-level registry (simple dict acting as our in-memory store)
# ---------------------------------------------------------------------------

_rooms: dict[str, RoomState] = {}


def create_room(creator_username: str) -> RoomState:
    room_id = uuid.uuid4().hex[:8].upper()
    room = RoomState(
        room_id=room_id,
        creator_username=creator_username,
        game=SonarGame(),
    )
    room.add_player(creator_username)
    _rooms[room_id] = room
    return room


def get_room(room_id: str) -> Optional[RoomState]:
    return _rooms.get(room_id)


def delete_room(room_id: str) -> None:
    _rooms.pop(room_id, None)
# sonar/models/game.py
# SonarGame — interface stub. Replace each method body with real game logic.

from typing import Any


class SonarGame:
    """
    Manages the state of a single Sonar game session.

    Attributes
    ----------
    bots : list[str]
        Bot difficulty levels currently in the room.
    """

    def __init__(self):
        self.language: str = "english"
        self.word_pack: str = "default"
        self.bots: list[str] = []
        self._scores: dict[str, int] = {}
        self._current_turn: str | None = None

    # ------------------------------------------------------------------
    # Settings (pre-game only)
    # ------------------------------------------------------------------

    def set_language(self, language: str) -> None:
        """Set the language used to pick the hidden word."""
        self.language = language

    def set_word_pack(self, word_pack: str) -> None:
        """Set the word pack / category."""
        self.word_pack = word_pack

    def set_bots(self, bots: list[str]) -> None:
        """
        Replace the bot roster.
        Each element must be one of: "noob", "pro", "hacker".
        """
        self.bots = bots

    # ------------------------------------------------------------------
    # Game flow
    # ------------------------------------------------------------------

    def start(self, player_usernames: list[str]) -> None:
        """
        Initialise the game: pick the hidden word, build turn order,
        reset scores. Called once when the creator sends START_GAME.

        Parameters
        ----------
        player_usernames : list[str]
            Human players in join order; bots are appended internally.
        """
        self._current_turn = player_usernames[0] if player_usernames else None
        self._scores = {u: 0 for u in player_usernames}

    def get_current_turn(self) -> str | None:
        """Return the username whose turn it currently is."""
        return self._current_turn

    def submit_guess(self, username: str, guess: str) -> dict[str, Any]:
        """
        Evaluate a player's guess against the hidden word.

        Returns
        -------
        dict with keys:
            "word_score"  (int) — points awarded for this specific guess
            "total_score" (int) — player's cumulative score
        """
        word_score = 0  # TODO: compute semantic similarity score
        self._scores[username] = self._scores.get(username, 0) + word_score
        return {"word_score": word_score, "total_score": self._scores[username]}

    def advance_turn(self) -> bool:
        """
        Move to the next player's turn.

        Returns
        -------
        bool
            True  — game continues.
            False — game is over.
        """
        # TODO: implement real turn rotation and win/end conditions
        return True

    def get_scores(self) -> dict[str, int]:
        """Return a dict mapping username → total score."""
        return dict(self._scores)
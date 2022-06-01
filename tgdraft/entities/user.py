"""Contains the definition for the User entity."""

from datetime import datetime
from typing import Any, Dict, List
from bson.objectid import ObjectId

from tgdraft.entities.cube import Cube


class User:
    """A simple user on our bot.

    Telegram chat_id will be our _id"""

    _id: ObjectId
    """
    Entity id on mongodb.

    Used as reference to this user in the bot.
    """

    chat_id: str
    """Chat_id for Telegram use."""

    username: str
    """
    User username from Telegram.

    .. note:
      In the future, users could modify their usernames since they are not used in any particular computation that need to be stored. The reference to a user will ever be his _id from mongodb.
    """

    cubes: list[Cube]
    """List of cubes owned by the user.
    """

    def __init__(
        self,
        chat_id: str = "",
        creation_date: datetime = datetime.now(),
        cubes: List[Cube] = [],
        username: str = "",
        _id: ObjectId = None,
    ) -> None:
        """Create a new instance of a user."""
        self.chat_id = chat_id
        self.creation_date = creation_date
        self.cubes = cubes

        if username:
            self.username = username

        if _id:
            self._id = _id

    @classmethod
    def from_dict(cls, dict: Dict[str, Any]):
        if not dict or not (chat_id := dict.get("chat_id")):
            return None

        return cls(
            chat_id=chat_id,
            creation_date=dict.get("creation_date"),
            username=dict.get("username"),
            _id=dict.get("_id"),
        )

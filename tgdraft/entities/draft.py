from datetime import datetime
from typing import List
from tgdraft.entities.user import User
from tgdraft.entities.cube import Cube

from bson.objectid import ObjectId


class Draft:
    def __init__(
        self,
        cube: Cube,
        players: int,
        date: datetime,
        code: str,
        chat_id: int,
        _id: ObjectId = None,
    ):
        """Create a new Draft entity.

        The value for _id if the entity is not in the database because it will be generated from Mongodb when the entity will be added."""
        self._id = _id
        self.cube = cube
        self.players = players
        self.date = date
        self.code = code
        self.chat_id = chat_id
        self.users: List[User] = []

    def set_date(self, date: datetime):
        self.date = date

    def set_code(self, code: str):
        self.code = code

    def sign_in(self, user: User):
        if user not in self.users:
            self.users.append(user)

    def sign_out(self, user: User):
        if user in self.users:
            self.users.pop(self.users.index(user))

    def save(self):
        result = db.drafts.insert_one(self.__dict__)
        if result.inserted_id:
            self._id = result.inserted_id

        return self

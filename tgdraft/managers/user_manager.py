from typing import Any, Dict
from tgdraft.entities.user import User
from bson.objectid import ObjectId
from datetime import datetime
from pymongo.database import Database


class UserManager:
    def __init__(self, db: Database):
        if db is None:
            raise ValueError("A valid database connection is required")
        self.db: Database = db

    def create(self, chat_id: int, username: str = "") -> User:
        """Create a new user in mongodb.

        :param chat_id: Chat Id of the user to create.
        :type chat_id: int
        :return: User created
        :rtype: User
        """
        if user := self.db.users.find_one({"chat_id": chat_id}):
            return User.from_dict(user)

        new = User(chat_id=chat_id, username=username)
        print(f"User: ", new.__dict__)
        ins = self.db.users.insert_one(new.__dict__)
        found = self.db.users.find_one({"_id": ins.inserted_id})
        return User.from_dict(found)

    def getByChatId(self, chat_id: int) -> User:
        """Retrieve a User from the database."""
        user = self.db.users.find_one({"chat_id": chat_id})
        return User.from_dict(user)

    def save(self, user: User) -> User:
        """Save a User in the database."""
        return self.db.users.find_one_and_update(
            {
                "_id": user._id,
            },
            {
                "$set": {
                    "chat_id": user.chat_id,
                    "username": user.username,
                    "update_date": datetime.now(),
                },
            },
        )

    def delete(self, user: User):
        self.db.users.delete_one({"_id": user._id})

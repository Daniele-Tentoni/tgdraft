"""Contains all the logic to connect to database and manage Draft documents."""

from datetime import datetime
import random
import string
from typing import Dict, Union
from tgdraft.entities.user import User
from tgdraft.entities.cube import Cube
from tgdraft.entities.draft import Draft

from pymongo.database import Database


class DraftManager:
    def __init__(self, db: Database):
        if db is None:
            raise ValueError("A valid database connection is required")
        self.db: Dict[str, Draft] = {}

    def getByCode(self, code: str):
        for k, draft in self.db.items():
            if draft.code == code:
                return draft
        return None

    def getById(self, _id) -> Draft:
        return self.db.get(_id, None)

    def create(
        self, cube, players: int, date: datetime, chat_id: int
    ) -> Draft:
        draft_code = self._produce_code()
        draft = Draft(
            cube=cube,
            players=players,
            date=date,
            code=draft_code,
            chat_id=chat_id,
        )
        self.db[draft_code] = draft  # code can't be the primary key
        return draft

    def sign_in(
        self, draft: Union[str, Draft], user: User
    ) -> Draft:  # From Python 3.10, could be str | Draft and str | User.
        """Sign a player to a draft."""

        _draft: Draft = (
            draft if type(draft) == Draft else self.getByCode(draft)
        )
        if not _draft:
            return None

        _draft.sign_in(user)
        return _draft

    def sign_out(self, code: str, user: User) -> Draft:
        draft = self.getByCode(code)
        draft.sign_out(user)
        return draft

    def _produce_code(self):
        """Produce a randomic 6 digit code.

        Use this code to identify temporaney drafts untils they come. After that, delete that code in the database."""
        N = 6
        code = "".join(
            random.SystemRandom().choice(string.ascii_uppercase)
            for _ in range(N)
        )
        # Check if the database contains that code
        return code

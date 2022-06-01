"""Contains all the logic to connect to database and manage Cube documents."""

from typing import Dict
from tgdraft.entities.cube import Cube
from tgdraft.entities.user import User

from pymongo.database import Database


class CubeManager:
    def __init__(self, db: Database):
        if db is None:
            raise ValueError("A valid database connection is required")
        self.db: Dict[str, Cube] = {}

    def confirm_cube_cobra_id(
        self, cobra_id: str, cube_chat_id: str, cube_name: str
    ):
        cube = self.getByName(chat_id=cube_chat_id, name=cube_name)
        cube.cobra_id = cobra_id

    def get_by_id(self, _id) -> Cube:
        return self.db.get(_id, None)

    def get_by_name(self, chat_id: str, name: str) -> Cube:
        for cube in self.db.values():
            if cube.chat_id == chat_id and cube.cube_name == name:
                return cube
        return None

    def save_cube(self, user: User, cube: Cube) -> Cube:
        cube.owner = user.chat_id
        user.cubes.append(cube)
        self.db[cube.cube_name] = cube
        return cube

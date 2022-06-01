"""Contains the definition for the Cube entity."""

from bson.objectid import ObjectId


class Cube:
    """A Cube to be drafted."""

    cobra_id: str
    """Id of cubecobra.com cube. Use it to link a cube to the respective object in Cube Cobra.
    """

    def __init__(
        self,
        chat_id: str,
        cube_name: str,
        owner: str,  # ObjectId of the user
        _id: ObjectId = None,
    ) -> None:
        self._id = _id
        self.chat_id = chat_id
        self.cube_name = cube_name
        self.owner = owner

    def move_to_another_chat(self, chat_id):
        self.chat_id = chat_id

    def set_cobra_link(self, link):
        self.cobra_link = link

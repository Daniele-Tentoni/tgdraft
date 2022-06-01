from unittest.mock import patch
import pytest
from tgdraft.entities.cube import Cube
from tgdraft.entities.user import User
from tgdraft.managers.cube_manager import CubeManager

starting_chat_id = "1"


@pytest.fixture
def simple_cube() -> Cube:
    return Cube("1", "N", "M")


@pytest.fixture
def simple_manager() -> CubeManager:
    return CubeManager(None)


@pytest.fixture
def manager_with_cubes() -> CubeManager:
    m = CubeManager(None)
    m.save_cube(User("1"), Cube("1", "1", "1"))
    m.save_cube(User("1"), Cube("1", "2", "1"))
    return m


def test_save_cube(simple_cube: Cube, simple_manager: CubeManager) -> None:
    simple_manager.save_cube(User("a"), simple_cube)
    assert simple_cube.cube_name in simple_manager.db.keys()
    assert simple_cube in simple_manager.db.values()


def test_get_by_name(
    simple_cube: Cube, manager_with_cubes: CubeManager
) -> None:
    first = manager_with_cubes.get_by_name("1", "1")
    second = manager_with_cubes.get_by_name("1", "2")
    assert first.cube_name == "1"
    assert second.cube_name == "2"


def test_get_nothing(manager_with_cubes: CubeManager) -> None:
    nothing = manager_with_cubes.get_by_name("2", "0")
    assert not nothing

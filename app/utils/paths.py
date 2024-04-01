import pathlib
from pathlib import Path

from app.utils import constants


def get_root_dir() -> str:
    current_dir = Path(__file__)
    return str(next(p for p in current_dir.parents if p.name == constants.APP_NAME))


def get_path(*args) -> str:
    return str(pathlib.PurePath(*args))

from config import POEMS_COUNT

from json import load
from typing import Any


poems: list[str] = []
poems_info: list[dict[str, Any]] = []


def init() -> None:
    for i in range(1, POEMS_COUNT + 1):
        poems.append(_get_poem(i))
        with open(f'data/poem_{i}_info.json', encoding='utf8') as json_file:
            poems_info.append(load(json_file))


def _get_poem(poem_number: int) -> str:
    poem_filename = f'divan/ghazal{poem_number}.txt'
    with open(poem_filename, encoding='utf8') as poem:
        return poem.read()


init()

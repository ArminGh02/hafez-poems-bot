import json
from typing import NamedTuple

import config


class Poem(NamedTuple):
    meter: str
    number: int
    related_songs: tuple[dict[str, str], ...]
    text: str


poems: tuple[Poem, ...]


def _init() -> None:
    poems_list = [None] * config.POEMS_COUNT
    for i in range(config.POEMS_COUNT):
        text = _get_poem_text(i + 1)
        with open(f'data/poem_{i + 1}_info.json', encoding='utf8') as json_file:
            poem_info = json.load(json_file)

        meter = poem_info['meter']
        related_songs = tuple(poem_info['relatedSongs'])
        poems_list[i] = Poem(meter, i, related_songs, text)

    global poems
    poems = tuple(poems_list)


def _get_poem_text(poem_number: int) -> str:
    with open(f'divan/ghazal{poem_number}.txt', encoding='utf8') as poem_file:
        return poem_file.read()


_init()

import json
from typing import NamedTuple

import config


class Song(NamedTuple):
    title: str
    link: str


class Poem(NamedTuple):
    meter: str
    number: int
    related_songs: tuple[Song, ...]
    text: str


poems: tuple[Poem, ...]


def _init() -> None:
    poems_list = [None] * config.POEMS_COUNT
    for i in range(config.POEMS_COUNT):
        with open(f'divan/ghazal{i + 1}.txt', encoding='utf8') as poem_file:
            text = poem_file.read()

        with open(f'data/poem_{i + 1}_info.json', encoding='utf8') as json_file:
            poem_info = json.load(json_file)

        meter = poem_info['meter']
        related_songs = tuple(map(lambda song: Song(song['title'], song['link'], poem_info['relatedSongs'])))

        poems_list[i] = Poem(meter, i, related_songs, text)

    global poems
    poems = tuple(poems_list)


_init()

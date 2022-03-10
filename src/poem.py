from typing import NamedTuple


class Song(NamedTuple):
    title: str
    link: str


class Poem(NamedTuple):
    meter: str
    number: int
    related_songs: tuple[Song, ...]
    text: str

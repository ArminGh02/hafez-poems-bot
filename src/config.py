import json
import re

import database
from poem import (
    Poem,
    Song,
)


with open('config.json') as _config_json:
    _config = json.load(_config_json)

API_TOKEN = _config['apiToken']
DATABASE_CHANNEL_USERNAME = _config['databaseChannelUsername']
DATABASE_HOST = _config['databaseHost']
DEVELOPER_USERNAME = _config['developerUsername']
GITHUB_REPO = _config['githubRepo']
POEMS_COUNT = _config['poemsCount']

INLINE_HELP = 'inline-help'
SEND_AUDIO = 'audio'
FAVORITE_POEMS_QUERY = '#favorite_poems'
SURROUNDED_WITH_DOUBLE_QUOTES = re.compile(r'^"[\u0600-\u06FF\s]+"$')
PERSIAN_WORDS = re.compile(r'^[\u0600-\u06FF\s]+$')
PERSIAN_YEH_MIDDLE_OF_WORD = re.compile(r'ی([^ ])')
NO_MATCH_WAS_FOUND = 'جستجو نتیجه ای در بر نداشت❗️'

poems: tuple[Poem, ...]
db = database.Handler(DATABASE_HOST)


def _init() -> None:
    poems_list = [None] * POEMS_COUNT
    for i in range(POEMS_COUNT):
        with open(f'divan/ghazal{i + 1}.txt', encoding='utf8') as poem_file:
            text = poem_file.read()
        with open(f'data/poem_{i + 1}_info.json', encoding='utf8') as json_file:
            poem_info = json.load(json_file)
        meter = poem_info['meter']
        related_songs = tuple(
            map(
                lambda song: Song(song['title'], song['link']),
                poem_info['relatedSongs'],
            )
        )
        poems_list[i] = Poem(meter, i, related_songs, text)

    global poems
    poems = tuple(poems_list)


_init()

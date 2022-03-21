import json
import re

import database
import search
from poem import Poem


with open('config.json') as _config_json:
    _config = json.load(_config_json)

API_TOKEN = _config['apiToken']
DATABASE_CHANNEL_USERNAME = _config['databaseChannelUsername']
DATABASE_HOST = _config['databaseHost']
DEVELOPER_USERNAME = _config['developerUsername']
GITHUB_REPO = _config['githubRepo']
POEMS_COUNT = _config['poemsCount']

BOT_USERNAME: str
INLINE_HELP = 'inline-help'
SEND_AUDIO = 'audio'
FAVORITE_POEMS_QUERY = '#favorite_poems'
SURROUNDED_WITH_DOUBLE_QUOTES = re.compile(r'^"[\u0600-\u06FF\s]+"$')
PERSIAN_WORDS = re.compile(r'^[\u0600-\u06FF\s]+$')
PERSIAN_YEH_MIDDLE_OF_WORD = re.compile(r'ی([^ ])')
NO_MATCH_WAS_FOUND = 'جستجو نتیجه ای در بر نداشت❗️'

poems: tuple[Poem, ...]
searcher = search.Searcher()
db = database.Handler(DATABASE_HOST)

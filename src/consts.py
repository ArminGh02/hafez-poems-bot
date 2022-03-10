import json

import database
import search


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
SURROUNDED_WITH_DOUBLE_QUOTES = r'^"[\u0600-\u06FF\s]+"$'
NO_MATCH_WAS_FOUND = 'جستجو نتیجه ای در بر نداشت❗️'

searcher = search.Searcher()
db = database.Handler(DATABASE_HOST)
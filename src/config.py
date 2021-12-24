from json import load


with open('config.json') as _config_json:
    _config = load(_config_json)


API_TOKEN = _config['apiToken']
POEMS_COUNT = _config['poemsCount']
DATABASE_CHANNEL_USERNAME = _config['databaseChannelUsername']
DATABASE_HOST = _config['databaseHost']

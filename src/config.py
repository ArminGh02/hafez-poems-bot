import json


with open('config.json') as _config_json:
    _config = json.load(_config_json)


API_TOKEN = _config['apiToken']
DATABASE_CHANNEL_USERNAME = _config['databaseChannelUsername']
DATABASE_HOST = _config['databaseHost']
DEVELOPER_USERNAME = _config['developerUsername']
GITHUB_REPO = _config['githubRepo']
POEMS_COUNT = _config['poemsCount']

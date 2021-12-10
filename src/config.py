from json import load


config = load(open('config.json'))

API_TOKEN = config['apiToken']
POEMS_COUNT = config['poemsCount']
DATABASE_CHANNEL_USERNAME = config['databaseChannelUsername']

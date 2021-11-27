from json import load


config = load(open('config.json'))

API_TOKEN = config['apiToken']

POEMS_DIRECTORY = config['poemsDirectory']
POEMS_COUNT = config['poemsCount']
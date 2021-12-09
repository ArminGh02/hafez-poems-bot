from config import POEMS_COUNT
from file_util import get_poem

import json
from typing import Any


poems: list[str] = []
poems_info: list[dict[str, Any]] = []


def init() -> None:
    for i in range(1, POEMS_COUNT + 1):
        poems.append(get_poem(i))
        with open('data/poem_%d_info.json' % i, encoding='utf8') as json_file:
            poems_info.append(json.load(json_file))


init()

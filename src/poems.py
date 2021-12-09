from config import POEMS_COUNT
from file_util import get_poem


poems: list[str] = []


def init() -> None:
    for i in range(1, POEMS_COUNT + 1):
        poems.append(get_poem(i))


init()

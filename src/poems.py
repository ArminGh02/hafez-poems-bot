from config import POEMS_COUNT

from json import load


class Poem:
    def __init__(self, meter: str, number: int, related_songs: tuple[dict[str, str], ...], text: str) -> None:
        self.meter = meter
        self.number = number
        self.related_songs = related_songs
        self.text = text

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Poem):
            return False
        return self.number == o.number

    def __hash__(self) -> int:
        return hash(self.number) ^ hash(self.text)


poems: tuple[Poem, ...]


def _init() -> None:
    poems_list = [None] * POEMS_COUNT
    for i in range(POEMS_COUNT):
        text = _get_poem_text(i + 1)
        with open(f'data/poem_{i + 1}_info.json', encoding='utf8') as json_file:
            poem_info = load(json_file)

        meter = poem_info['meter']
        related_songs = tuple(poem_info['relatedSongs'])
        poems_list[i] = Poem(meter, i, related_songs, text)

    global poems
    poems = tuple(poems_list)


def _get_poem_text(poem_number: int) -> str:
    poem_filename = f'divan/ghazal{poem_number}.txt'
    with open(poem_filename, encoding='utf8') as poem_file:
        return poem_file.read()


_init()

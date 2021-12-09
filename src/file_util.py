from config import POEMS_DIRECTORY


def get_poem(poem_number: int) -> str:
    poem_filename = POEMS_DIRECTORY + '/ghazal%d.txt' % poem_number
    with open(poem_filename, encoding='utf8') as poem:
        return poem.read()

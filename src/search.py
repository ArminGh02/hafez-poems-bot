from config import POEMS_COUNT
from file_util import get_poem

from typing import (
    Callable,
    Union,
)


class Searcher:
    def search_return_lines(
            self,
            to_search: Union[str, list[str]],
            index_of_matched_line: Union[Callable[[list[str], str], int], Callable[[list[str], list[str]], int]],
    ) -> list[str]:
        results = []
        for i in range(1, POEMS_COUNT + 1):
            lines = get_poem(i).splitlines()
            j = index_of_matched_line(lines, to_search)
            if j > -1:
                result = lines[j - 1] + '\n' + lines[j] + '\n' + lines[j + 1]
                results.append(result)

        return results

    def search_return_poems(
            self,
            to_search: Union[str, list[str]],
            index_of_matched_line: Union[Callable[[list[str], str], int], Callable[[list[str], list[str]], int]],
    ) -> list[tuple[int, str]]:
        results = []
        for i in range(1, POEMS_COUNT + 1):
            poem = get_poem(i)
            lines = poem.splitlines()
            j = index_of_matched_line(lines, to_search)
            if j > -1:
                results.append((i, poem))

        return results


def index_of_matched_line_words(lines: list[str], words_to_search: list[str]) -> int:
    for i, line in enumerate(lines):
        if all(word in line for word in words_to_search):
            return i
    return -1


def index_of_matched_line_string(lines: list[str], to_search: str) -> int:
    for i, line in enumerate(lines):
        if to_search in line:
            return i
    return -1

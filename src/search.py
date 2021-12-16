from poems import (
    Poem,
    poems,
)

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
        for poem in poems:
            lines = poem.text.splitlines()
            j = index_of_matched_line(lines, to_search)
            if j > -1:
                result = lines[j - 1] + '\n' + lines[j] + '\n' + lines[j + 1]
                results.append(result)

        return results

    def search_return_poems(
            self,
            to_search: Union[str, list[str]],
            index_of_matched_line: Union[Callable[[list[str], str], int], Callable[[list[str], list[str]], int]],
    ) -> list[Poem]:
        results = []
        for poem in poems:
            lines = poem.text.splitlines()
            j = index_of_matched_line(lines, to_search)
            if j > -1:
                results.append(poem)

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

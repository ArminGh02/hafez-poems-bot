from typing import (
    Callable,
    Union,
)

import config
from poem import Poem


class Searcher:
    @staticmethod
    def matching_lines(to_search: Union[str, list[str]]) -> list[str]:
        index_of = Searcher._index_of(to_search)
        results = []
        for poem in config.poems:
            lines = poem.text.splitlines()
            i = index_of(lines, to_search)
            if i >= 0:
                res = lines[i - 1] + '\n' + lines[i] + '\n' + lines[i + 1]
                results.append(res)
        return results

    @staticmethod
    def matching_poems(to_search: Union[str, list[str]]) -> list[Poem]:
        index_of = Searcher._index_of(to_search)
        results = []
        for poem in config.poems:
            lines = poem.text.splitlines()
            if index_of(lines, to_search) >= 0:
                results.append(poem)
        return results

    @staticmethod
    def matching_poems_and_lines(to_search: Union[str, list[str]], limit: int = -1) -> list[Union[str, Poem]]:
        index_of = Searcher._index_of(to_search)
        results = []
        found = 0
        for poem in config.poems:
            if found >= limit >= 0:
                break
            lines = poem.text.splitlines()
            i = index_of(lines, to_search)
            if i >= 0:
                res = lines[i - 1] + '\n' + lines[i] + '\n' + lines[i + 1]
                results.append(res)
                results.append(poem)
                found += 1
        return results

    @staticmethod
    def _index_of(to_search: str) -> Union[Callable[[list[str], str], int], Callable[[list[str], list[str]], int]]:
        if isinstance(to_search, str):
            return Searcher._index_of_string
        if isinstance(to_search, list):
            return Searcher._index_of_words
        raise TypeError(f'unsupported type {type(to_search)}')

    @staticmethod
    def _index_of_words(lines: list[str], words_to_search: list[str]) -> int:
        for i, line in enumerate(lines):
            if all(word in line for word in words_to_search):
                return i
        return -1

    @staticmethod
    def _index_of_string(lines: list[str], to_search: str) -> int:
        for i, line in enumerate(lines):
            if to_search in line:
                return i
        return -1

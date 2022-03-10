from typing import Any

import pymongo


class Handler:
    def __init__(self, host: str) -> None:
        client = pymongo.MongoClient(host)
        db = client['hafez_bot']
        self.__users = db['users']

    def add_user(self, user_id: int) -> None:
        if not self.__users.find_one({'user_id': user_id}):
            self.__users.insert_one({'user_id': user_id, 'favorite_poems': ''})

    def users_count(self) -> int:
        return self.__users.count_documents({})

    def get_favorite_poems(self, user_id: int) -> set[int]:
        user = self.__users.find_one({'user_id': user_id})
        return set(user['favorite_poems'])

    def add_to_favorite_poems(self, user_id: int, poem_index: int) -> None:
        favorite_poems = self.get_favorite_poems(user_id)
        favorite_poems.add(poem_index)
        self.__users.update_one({'user_id': user_id}, {'$set': {'favorite_poems': tuple(favorite_poems)}})

    def remove_from_favorite_poems(self, user_id: int, poem_index: int) -> None:
        favorite_poems = self.get_favorite_poems(user_id)
        favorite_poems.remove(poem_index)
        self.__users.update_one({'user_id': user_id}, {'$set': {'favorite_poems': tuple(favorite_poems)}})

    def is_reply_with_line(self, user_id: int, default: Any = None) -> Any:
        user = self.__users.find_one({'user_id': user_id})
        return user.get('reply_with_line', default)

    def set_reply_with_line(self, user_id: int, value: bool) -> None:
        self.__users.update_one({'user_id': user_id}, {'$set': {'reply_with_line': value}})

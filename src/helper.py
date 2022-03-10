import random
from typing import Union

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    User,
)

import consts
import search
from poems import (
    Poem,
    poems
)


def build_poem_keyboard(poem: Poem, user: User, inline: bool) -> InlineKeyboardMarkup:
    if inline:
        audio_button = InlineKeyboardButton(
            text='خوانش 🗣',
            url=f'https://telegram.me/{consts.BOT_USERNAME}?start={consts.SEND_AUDIO}{poem.number}'
        )
    else:
        audio_button = InlineKeyboardButton('خوانش 🗣', callback_data=f'audio{poem.number}')

    keyboard = [[audio_button]]

    if poem.related_songs:
        related_songs_button = InlineKeyboardButton(
            text='این شعر را چه کسی در کدام آهنگ خوانده است؟ 🎵',
            callback_data=f'songs{poem.number}'
        )
        keyboard.append([related_songs_button])

    if poem.number in consts.db.get_favorite_poems(user.id):
        keyboard.append(
            [InlineKeyboardButton('حذف از غزل‌های مورد علاقه', callback_data=f'remove{poem.number}')]
        )
    else:
        keyboard.append(
            [InlineKeyboardButton('افزودن به غزل های مورد علاقه ❤️', callback_data=f'add{poem.number}')]
        )

    return InlineKeyboardMarkup(keyboard)


def get_random_poem() -> Poem:
    return poems[random.randrange(0, consts.POEMS_COUNT - 1)]


def search_impl(update: Update, query: Union[str, list[str]]) -> None:
    user = update.effective_user
    results = find_results(update, query)
    if not results:
        update.effective_chat.send_message(consts.NO_MATCH_WAS_FOUND)
    elif consts.db.is_reply_with_line(user.id, True):
        for poem in results:
            update.effective_chat.send_message(poem)
    else:
        for poem in results:
            update.effective_chat.send_message(
                text=poem.text + '🎼وزن: ' + poem.meter,
                reply_markup=build_poem_keyboard(poem, user, False),
            )


def find_results(update: Update, to_search: Union[str, list[str]]) -> Union[list[str], list[Poem]]:
    if isinstance(to_search, str):
        index_of_matched_line = search.index_of_matched_line_string
    else:
        index_of_matched_line = search.index_of_matched_line_words

    if consts.db.is_reply_with_line(update.effective_user.id, True):
        results = consts.searcher.search_return_lines(to_search, index_of_matched_line)
    else:
        results = consts.searcher.search_return_poems(to_search, index_of_matched_line)

    return results


def choose_result_mode(update: Update, query: str) -> None:
    update.message.reply_text(
        text='لطفا انتخاب کن:',
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('در نتیجه جستجو، کل غزل دریافت شود.', callback_data=f'poem_{query}')],
                [InlineKeyboardButton('در نتیجه جستجو، فقط بیت دریافت شود.', callback_data=f'line_{query}')],
            ]
        )
    )

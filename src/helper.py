import random
from typing import Union

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    User,
)

import config
from search import Searcher
from poem import Poem


def build_poem_keyboard(poem: Poem, user: User, bot_username: str, inline: bool) -> InlineKeyboardMarkup:
    if inline:
        audio_button = InlineKeyboardButton(
            text='خوانش 🗣',
            url=f'https://telegram.me/{bot_username}?start={config.SEND_AUDIO}{poem.number}'
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

    if poem.number in config.db.favorite_poems(user.id):
        keyboard.append(
            [InlineKeyboardButton('حذف از غزل‌های مورد علاقه', callback_data=f'remove{poem.number}')]
        )
    else:
        keyboard.append(
            [InlineKeyboardButton('افزودن به غزل های مورد علاقه ❤️', callback_data=f'add{poem.number}')]
        )

    return InlineKeyboardMarkup(keyboard)


def random_poem() -> Poem:
    return config.poems[random.randrange(0, config.POEMS_COUNT - 1)]


def search_impl(update: Update, query: Union[str, list[str]], bot_username: str) -> None:
    user = update.effective_user
    results = find_results(update, query)
    if not results:
        update.effective_chat.send_message(config.NO_MATCH_WAS_FOUND)
    elif config.db.reply_with_line(user.id, True):
        for poem in results:
            update.effective_chat.send_message(poem)
    else:
        for poem in results:
            update.effective_chat.send_message(
                text=poem.text + '🎼وزن: ' + poem.meter,
                reply_markup=build_poem_keyboard(poem, user, bot_username, False),
            )


def find_results(update: Update, to_search: Union[str, list[str]]) -> Union[list[str], list[Poem]]:
    if config.db.reply_with_line(update.effective_user.id, True):
        return Searcher.matching_lines(to_search)
    else:
        return Searcher.matching_poems(to_search)


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


def make_yeh_arabic(s: str) -> str:
    return config.PERSIAN_YEH_MIDDLE_OF_WORD.sub(r'ي\1', s)

from config import (
    API_TOKEN,
    DATABASE_CHANNEL_USERNAME,
    DATABASE_HOST,
    POEMS_COUNT,
)
from db import DatabaseHandler
from poems import (
    Poem,
    poems,
)
from search import (
    Searcher,
    index_of_matched_line_string,
    index_of_matched_line_words,
)

from random import randrange
from re import match
from typing import Union
from uuid import uuid4

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
    User,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    InlineQueryHandler,
    MessageHandler,
    Updater,
)


_BOT_USERNAME: str
_INLINE_HELP = 'inline-help'
_SEND_AUDIO = 'audio'
_FAVORITE_POEMS_QUERY = '#favorite_poems'
_SURROUNDED_WITH_DOUBLE_QUOTES = r'^"[\u0600-\u06FF\s]+"$'
_NO_MATCH_WAS_FOUND = 'جستجو نتیجه ای در بر نداشت❗️'

_searcher = Searcher()
_db = DatabaseHandler(DATABASE_HOST)


############################
# CommandHandler callbacks #
############################

def start(update: Update, context: CallbackContext) -> None:
    args = context.args
    if args:
        if args[0] == _INLINE_HELP:
            update.message.reply_text(
                'بعد از نوشتن یوزرنیمِ بات در یک چت،\n'
                'با نوشتن چند کلمه از یک بیت حافظ، غزل یا بیتی را که\n'
                'یک بیتش شامل کلمات وارد شده، باشد دریافت خواهی کرد.\n'
                'در ضمن اگر می خواهی کل یک عبارت با هم (و نه تک تک کلماتش)\n'
                'در بیت جستجو شود، آن را درون "" بگذار.'
            )
        elif args[0].startswith(_SEND_AUDIO):
            poem_number = int(args[0].removeprefix(_SEND_AUDIO))
            context.bot.forward_message(
                chat_id=update.effective_chat.id,
                from_chat_id=DATABASE_CHANNEL_USERNAME,
                message_id=poem_number + 2   # channel message ID's start from 2
            )
    else:
        help_command(update, context)
        _db.add_user(update.effective_user.id)


def help_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(
        f'سلام {update.effective_user.first_name}!\n'
        'با نوشتن چند کلمه از یک بیت حافظ، غزل یا بیتی را که \n'
        'یک بیتش شامل کلمات وارد شده، باشد دریافت خواهی کرد.\n'
        'در ضمن اگر می خواهی کل یک عبارت با هم (و نه تک تک کلماتش)\n'
        'در بیت جستجو شود، آن را درون "" بگذار.\n'
        'همچنین با زدن دستور /fal یک فال می توانی بگیری.\n'
        f'تعداد کاربران: {_db.users_count()}',
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton('Github', 'https://github.com/ArminGh02/hafez-poems-telegram-bot'),
                InlineKeyboardButton('Developer', 'https://telegram.me/ArminGh02'),
            ],
        ]),
    )


def reply_line(update: Update, _: CallbackContext) -> None:
    _db.reply_with_line(update.effective_user.id)
    update.message.reply_text('از این پس در نتیجه جستجو، بیت را دریافت خواهی کرد.✅')


def reply_poem(update: Update, _: CallbackContext) -> None:
    _db.reply_with_poem(update.effective_user.id)
    update.message.reply_text('از این پس در نتیجه جستجو، کل غزل را دریافت خواهی کرد.✅')


def random_poem_command(update: Update, _: CallbackContext) -> None:
    poem = get_random_poem()
    update.message.reply_text(
        text=poem.text + '🎼وزن: ' + poem.meter,
        reply_markup=build_poem_keyboard(poem, update.effective_user, False),
    )


def list_favorite_poems(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(
        text='دکمه زیر را بزن.',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        'لیست غزل های مورد علاقه ❤️',
                        switch_inline_query_current_chat=_FAVORITE_POEMS_QUERY
                    )
                ],
            ]
        ),
    )


############################
# MessageHandler callbacks #
############################

def search_words(update: Update, _: CallbackContext) -> None:
    query = update.message.text
    if _db.is_reply_with_line(update.effective_user.id) is None:
        choose_result_mode(update, query)
        return

    search_impl(update, query.split())


def search_string(update: Update, _: CallbackContext) -> None:
    query = update.message.text
    if _db.is_reply_with_line(update.effective_user.id) is None:
        choose_result_mode(update, query)
        return

    search_impl(update, query[1:-1])


##################################
# CallbackQueryHandler callbacks #
##################################

def result_mode_chosen(update: Update, _: CallbackContext) -> None:
    user = update.effective_user
    query = update.callback_query
    data = query.data

    if data.startswith('line_'):
        text = 'در نتیجه جستجو بیت دریافت می شود.'
        _db.set_reply_with_line(user.id, True)
        search_query = data.removeprefix('line_')
    else:  # data == 'poem_<query>'
        text = 'در نتیجه جستجو کل غزل دریافت می شود.'
        _db.set_reply_with_line(user.id, False)
        search_query = data.removeprefix('poem_')

    query.edit_message_text(text)
    query.answer()

    if search_query.startswith('"'):
        search_impl(update, search_query[1:-1])
    else:
        search_impl(update, search_query.split())


def add_to_favorite_poems(update: Update, _: CallbackContext) -> None:
    user = update.effective_user
    query = update.callback_query

    poem_number = int(query.data.removeprefix('add'))

    _db.add_to_favorite_poems(user.id, poem_number)

    query.edit_message_reply_markup(build_poem_keyboard(poems[poem_number], user, update.effective_chat == None))
    query.answer('این غزل به لیست علاقه‌مندی‌های شما افزوده شد.')


def remove_from_favorite_poems(update: Update, _: CallbackContext) -> None:
    user = update.effective_user
    query = update.callback_query

    poem_number = int(query.data.removeprefix('remove'))

    _db.remove_from_favorite_poems(user.id, poem_number)

    query.edit_message_reply_markup(build_poem_keyboard(poems[poem_number], user, update.effective_chat == None))
    query.answer('این غزل از لیست علاقه‌مندی‌های شما حذف شد.')


def send_audio_of_poem(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    poem_number = int(query.data.removeprefix('audio'))

    context.bot.forward_message(
        chat_id=update.effective_chat.id,
        from_chat_id=DATABASE_CHANNEL_USERNAME,
        message_id=poem_number + 2   # channel message ID's start from 2
    )

    query.answer()


def display_related_songs_to_poem(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    poem_number = int(query.data.removeprefix('songs'))

    related_songs = poems[poem_number].related_songs

    keyboard = [
        *map(
            lambda song: [InlineKeyboardButton(song['title'], url=song['link'])],
            related_songs
        ),
        [InlineKeyboardButton('بازگشت 🔙', callback_data=f'back{poem_number}')]
    ]

    query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))
    query.answer()


def return_to_menu_of_poem(update: Update, _:CallbackContext) -> None:
    query = update.callback_query
    poem_number = int(query.data.removeprefix('back'))
    user = update.effective_user

    query.edit_message_reply_markup(build_poem_keyboard(poems[poem_number], user, update.effective_chat == None))
    query.answer()


################################
# InlineQueryHandler callbacks #
################################

def handle_favorite_poems_inline_query(update: Update, _: CallbackContext) -> None:
    user = update.effective_user
    favorite_poems = map(lambda poem_number: poems[poem_number], _db.get_favorite_poems(user.id))

    if not favorite_poems:
        update.inline_query.answer(
            results=[],
            switch_pm_text='لیست علاقه‌مندی‌های شما خالی است ❗️',
            switch_pm_parameter='no-favorite-poems',
        )
        return

    results = list(
        map(
            lambda poem: InlineQueryResultArticle(
                id=str(uuid4()),
                title=poem.text,
                input_message_content=InputTextMessageContent(poem.text + '🎼وزن: ' + poem.meter),
                reply_markup=build_poem_keyboard(poem, user, True),
            ),
            favorite_poems
        )
    )

    update.inline_query.answer(results, cache_time=3)


def handle_inline_query(update: Update, _: CallbackContext) -> None:
    query = update.inline_query.query
    user = update.effective_user

    persian_words = r'^[\u0600-\u06FF\s]+$'
    search_results = []
    if match(_SURROUNDED_WITH_DOUBLE_QUOTES, query):
        search_results = find_results(update, query[1:-1])
    elif match(persian_words, query):
        search_results = find_results(update, query.split())

    poem = get_random_poem()
    random_poem_article = InlineQueryResultArticle(
        id=str(uuid4()),
        title='فال 🎲',
        input_message_content=InputTextMessageContent(poem.text),
        reply_markup=build_poem_keyboard(poem, user, True),
    )

    if not search_results:
        update.inline_query.answer(
            results=[random_poem_article],
            switch_pm_text=_NO_MATCH_WAS_FOUND,
            switch_pm_parameter=_INLINE_HELP
        )
        return

    if _db.is_reply_with_line(user.id, True):
        results = [
            random_poem_article,
            *map(
                lambda search_result: InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=search_result,
                    input_message_content=InputTextMessageContent(search_result),
                ),
                search_results
            ),
        ]
    else:
        results = [
            random_poem_article,
            *map(
                lambda poem: InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=poem.text,
                    input_message_content=InputTextMessageContent(
                        poem.text + '🎼وزن: ' + poem.meter
                    ),
                    reply_markup=build_poem_keyboard(poem, user, True),
                ),
                search_results
            ),
        ]

    update.inline_query.answer(results, cache_time=3, switch_pm_text='راهنما ❓', switch_pm_parameter=_INLINE_HELP)


####################
# Helper functions #
####################


def build_poem_keyboard(poem: Poem, user: User, inline: bool) -> InlineKeyboardMarkup:
    if inline:
        audio_button = InlineKeyboardButton(
            text='خوانش 🗣',
            url=f'https://telegram.me/{_BOT_USERNAME}?start={_SEND_AUDIO}{poem.number}'
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

    if poem.number in _db.get_favorite_poems(user.id):
        keyboard.append(
            [InlineKeyboardButton('حذف از غزل‌های مورد علاقه', callback_data=f'remove{poem.number}')]
        )
    else:
        keyboard.append(
            [InlineKeyboardButton('افزودن به غزل های مورد علاقه ❤️', callback_data=f'add{poem.number}')]
        )

    return InlineKeyboardMarkup(keyboard)


def get_random_poem() -> Poem:
    rand = randrange(0, POEMS_COUNT - 1)
    return poems[rand]


def search_impl(update: Update, query: Union[str, list[str]]) -> None:
    user = update.effective_user
    results = find_results(update, query)
    if not results:
        update.effective_chat.send_message(_NO_MATCH_WAS_FOUND)
    elif _db.is_reply_with_line(user.id, True):
        for poem in results:
            update.effective_chat.send_message(poem)
    else:
        for poem in results:
            update.effective_chat.send_message(
                text=poem.text + '🎼وزن: ' + poem.meter,
                reply_markup=build_poem_keyboard(poem, user, False),
            )


def find_results(update: Update, to_search: Union[str, list[str]]) -> Union[list[str], list[Poem]]:
    index_of_matched_line = index_of_matched_line_string if isinstance(to_search, str) else index_of_matched_line_words
    if _db.is_reply_with_line(update.effective_user.id, True):
        results = _searcher.search_return_lines(to_search, index_of_matched_line)
    else:
        results = _searcher.search_return_poems(to_search, index_of_matched_line)

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


def main() -> None:
    updater = Updater(API_TOKEN)
    dispatcher = updater.dispatcher
    bot = updater.bot

    global _BOT_USERNAME
    _BOT_USERNAME = bot.username

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('faal', random_poem_command))
    dispatcher.add_handler(CommandHandler('favorite', list_favorite_poems))
    dispatcher.add_handler(CommandHandler('ghazal', reply_poem))
    dispatcher.add_handler(CommandHandler('beit', reply_line))

    dispatcher.add_handler(MessageHandler(Filters.regex(_SURROUNDED_WITH_DOUBLE_QUOTES), search_string))
    dispatcher.add_handler(
        MessageHandler(
            Filters.text & ~Filters.command & ~Filters.via_bot(username=_BOT_USERNAME),
            search_words,
        )
    )

    dispatcher.add_handler(CallbackQueryHandler(result_mode_chosen, pattern=r'^(poem_|line_)'))
    dispatcher.add_handler(CallbackQueryHandler(add_to_favorite_poems, pattern=r'^add\d{1,3}$'))
    dispatcher.add_handler(CallbackQueryHandler(remove_from_favorite_poems, pattern=r'^remove\d{1,3}$'))
    dispatcher.add_handler(CallbackQueryHandler(send_audio_of_poem, pattern=r'^audio\d{1,3}$'))
    dispatcher.add_handler(CallbackQueryHandler(display_related_songs_to_poem, pattern=r'^songs\d{1,3}$'))
    dispatcher.add_handler(CallbackQueryHandler(return_to_menu_of_poem, pattern=r'^back\d{1,3}$'))

    dispatcher.add_handler(InlineQueryHandler(handle_favorite_poems_inline_query, pattern=_FAVORITE_POEMS_QUERY))
    dispatcher.add_handler(InlineQueryHandler(handle_inline_query))

    bot.set_my_commands(
        [
            ('start', 'بات را ری‌استارت می‌کند'),
            ('help', 'راهنما'),
            ('faal', 'یک فال حافظ می‌گیرد'),
            ('favorite', 'لیست غزل های مورد علاقه را نشان می‌دهد'),
            ('ghazal', 'در نتیجه جستجو کل غزل را می‌فرستد'),
            ('beit', 'در نتیجه جستجو فقط بیت را می‌فرستد'),
        ]
    )

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

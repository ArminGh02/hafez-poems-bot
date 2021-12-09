from poems import poems
from config import (
    API_TOKEN,
    POEMS_COUNT,
)

from random import randrange
from re import match
from typing import (
    Callable,
    Union,
)
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


INLINE_HELP = 'inline-help'
FAVORITE_POEMS_QUERY = '#favorite_poems'
SURROUNDED_WITH_DOUBLE_QUOTES = r'^"[\u0600-\u06FF\s]+"$'
NO_MATCH_WAS_FOUND = 'جستجو نتیجه ای در بر نداشت❗️'

searcher = Searcher()
user_to_favorite_poems: dict[User, set[str]] = {}
user_to_reply_with_line: dict[User, bool] = {}
to_invoke: Callable[[], None]


from search import (
    Searcher,
    index_of_matched_line_string,
    index_of_matched_line_words,
)


def start(update: Update, context: CallbackContext) -> None:
    args = context.args
    if args:
        if args[0] == INLINE_HELP:
            update.message.reply_text(
                'بعد از نوشتن یوزرنیمِ بات در یک چت،\n'
                'با نوشتن چند کلمه از یک بیت حافظ، غزل یا بیتی را که\n'
                'یک بیتش شامل کلمات وارد شده، باشد دریافت خواهی کرد.\n'
                'در ضمن اگر می خواهی کل یک عبارت با هم (و نه تک تک کلماتش)\n'
                'در بیت جستجو شود، آن را درون "" بگذار.'
            )
    else:
        help_command(update, context)
        user_to_favorite_poems[update.effective_user] = set()


def help_command(update: Update, _: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton('Github', 'https://github.com/ArminGh02/hafez-poems-telegram-bot'),
            InlineKeyboardButton('Developer', 'https://telegram.me/ArminGh02'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        f'سلام {update.effective_user.first_name}!\n'
        'با نوشتن چند کلمه از یک بیت حافظ، غزل یا بیتی را که \n'
        'یک بیتش شامل کلمات وارد شده، باشد دریافت خواهی کرد.\n'
        'در ضمن اگر می خواهی کل یک عبارت با هم (و نه تک تک کلماتش)\n'
        'در بیت جستجو شود، آن را درون "" بگذار.\n'
        'همچنین با زدن دستور /fal یک فال می توانی بگیری.\n'
        f'تعداد کاربران: {max(len(user_to_reply_with_line), len(user_to_favorite_poems))}',
        reply_markup=reply_markup,
    )


def reply_line(update: Update, _: CallbackContext) -> None:
    user_to_reply_with_line[update.effective_user] = True
    update.message.reply_text('از این پس در نتیجه جستجو، بیت را دریافت خواهی کرد.✅')


def reply_poem(update: Update, _: CallbackContext) -> None:
    user_to_reply_with_line[update.effective_user] = False
    update.message.reply_text('از این پس در نتیجه جستجو، کل غزل را دریافت خواهی کرد.✅')


def random_poem_command(update: Update, _: CallbackContext) -> None:
    poem_number, poem = get_random_poem()
    update.message.reply_text(poem, reply_markup=get_poem_keyboard(poem_number, poem, update.effective_user))


def get_poem_keyboard(poem_number: int, poem: str, user: User) -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]]
    if user in user_to_favorite_poems and (poem_number, poem) in user_to_favorite_poems[user]:
        callback_data = 'remove' + str(poem_number)
        keyboard = [[InlineKeyboardButton('حذف از غزل‌های مورد علاقه', callback_data=callback_data)]]
    else:
        callback_data = 'add' + str(poem_number)
        keyboard = [[InlineKeyboardButton('افزودن به غزل های مورد علاقه ❤️', callback_data=callback_data)]]

    return InlineKeyboardMarkup(keyboard)


def get_random_poem() -> tuple[int, str]:
    rand = randrange(0, POEMS_COUNT - 1)
    return rand, poems[rand]


def list_favorite_poems(update: Update, _: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton('لیست غزل های مورد علاقه ❤️', switch_inline_query_current_chat=FAVORITE_POEMS_QUERY)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('دکمه زیر را بزن.', reply_markup=reply_markup)


def search_words(update: Update, _: CallbackContext) -> None:
    words = update.message.text.split()
    search_impl(update, words)


def search_string(update: Update, _: CallbackContext) -> None:
    string_to_search = update.message.text[1:-1]  # remove "" (double quotes) from start and end of string
    search_impl(update, string_to_search)


def search_impl(update: Update, to_search: Union[str, list[str]]) -> None:
    user = update.effective_user

    def send_results() -> None:
        results = find_results(update, to_search)
        if not results:
            update.message.reply_text(NO_MATCH_WAS_FOUND)
        elif user_to_reply_with_line[user]:
            for poem in results:
                update.message.reply_text(poem)
        else:
            for poem_number, poem in results:
                update.message.reply_text(poem, reply_markup=get_poem_keyboard(poem_number, poem, user))

    if user not in user_to_reply_with_line:
        choose_result_mode(update)
        global to_invoke
        to_invoke = send_results
    else:
        send_results()


def find_results(update: Update, to_search: Union[str, list[str]]) -> Union[list[str], list[tuple[str]]]:
    user = update.effective_user

    if user not in user_to_reply_with_line:
        user_to_reply_with_line[user] = True

    results: Union[list[str], list[tuple[int, str]]]
    index_of_matched_line = index_of_matched_line_string if isinstance(to_search, str) else index_of_matched_line_words
    if user_to_reply_with_line[user]:
        results = searcher.search_return_lines(to_search, index_of_matched_line)
    else:
        results = searcher.search_return_poems(to_search, index_of_matched_line)

    return results


def choose_result_mode(update: Update) -> None:
    keyboard = [
        [InlineKeyboardButton('در نتیجه جستجو، کل غزل دریافت شود.', callback_data='poem')],
        [InlineKeyboardButton('در نتیجه جستجو، فقط بیت دریافت شود.', callback_data='line')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('لطفا انتخاب کن:', reply_markup=reply_markup)


def result_mode_chosen(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    user = update.effective_user

    text: str
    if query.data == 'line':
        text = 'در نتیجه جستجو بیت دریافت می شود.'
        user_to_reply_with_line[user] = True
    else:  # query.data == 'poem'
        text = 'در نتیجه جستجو کل غزل دریافت می شود.'
        user_to_reply_with_line[user] = False

    query.edit_message_text(text)
    query.answer()
    to_invoke()


def add_to_favorite_poems(update: Update, _: CallbackContext) -> None:
    user = update.effective_user
    query = update.callback_query

    poem_number = int(query.data.removeprefix('add'))
    if user not in user_to_favorite_poems:
        user_to_favorite_poems[user] = {(poem_number, poems[poem_number])}
    else:
        user_to_favorite_poems[user].add((poem_number, poems[poem_number]))

    query.edit_message_reply_markup(get_poem_keyboard(poem_number, poems[poem_number], user))
    query.answer('این غزل به لیست علاقه‌مندی‌های شما افزوده شد.')


def remove_from_favorite_poems(update: Update, _: CallbackContext) -> None:
    user = update.effective_user
    query = update.callback_query

    poem_number = int(query.data.removeprefix('remove'))
    user_to_favorite_poems[user].remove((poem_number, poems[poem_number]))

    query.edit_message_reply_markup(get_poem_keyboard(poem_number, poems[poem_number], user))
    query.answer('این غزل از لیست علاقه‌مندی‌های شما حذف شد.')


def handle_favorite_poems_inline_query(update: Update, _: CallbackContext) -> None:
    user = update.effective_user
    if not user_to_favorite_poems.get(user):
        update.inline_query.answer(
            results=[],
            switch_pm_text='لیست علاقه‌مندی‌های شما خالی است ❗️',
            switch_pm_parameter='no-favorite-poems',
        )
        return

    favorite_poems = user_to_favorite_poems[user]
    results = []
    for poem_number, poem in favorite_poems:
        results.append(
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=poem[:60] + '...',
                input_message_content=InputTextMessageContent(poem),
                reply_markup=get_poem_keyboard(poem_number, poem, user),
            )
        )

    update.inline_query.answer(results, cache_time=3)


def handle_inline_query(update: Update, _: CallbackContext) -> None:
    query = update.inline_query.query
    user = update.effective_user

    persian_words = r'^[\u0600-\u06FF\s]+$'
    search_results = []
    if match(SURROUNDED_WITH_DOUBLE_QUOTES, query):
        search_results = find_results(update, query[1:-1])
    elif match(persian_words, query):
        search_results = find_results(update, query.split())

    poem_number, poem = get_random_poem()
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title='فال',
            input_message_content=InputTextMessageContent(poem),
            reply_markup=get_poem_keyboard(poem_number, poem, user),
        ),
    ]

    if not search_results:
        update.inline_query.answer(results, switch_pm_text=NO_MATCH_WAS_FOUND, switch_pm_parameter=INLINE_HELP)
        return

    if user in user_to_reply_with_line and user_to_reply_with_line[user]:
        for search_result in search_results:
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=search_result[:60] + '...',
                    input_message_content=InputTextMessageContent(search_result),
                )
            )
    else:
        for poem_number, poem in search_results:
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=poem[:60] + '...',
                    input_message_content=InputTextMessageContent(poem),
                    reply_markup=get_poem_keyboard(poem_number, poem, user),
                )
            )

    update.inline_query.answer(results, cache_time=3, switch_pm_text='راهنما ❓', switch_pm_parameter=INLINE_HELP)


def main() -> None:
    updater = Updater(API_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('fal', random_poem_command))
    dispatcher.add_handler(CommandHandler('ghazal', reply_poem))
    dispatcher.add_handler(CommandHandler('beit', reply_line))
    dispatcher.add_handler(CommandHandler('favorite', list_favorite_poems))

    dispatcher.add_handler(MessageHandler(Filters.regex(SURROUNDED_WITH_DOUBLE_QUOTES), search_string))
    dispatcher.add_handler(
        MessageHandler(
            Filters.text & ~Filters.command & ~Filters.via_bot(username='hafez_poems_bot'),
            search_words
        )
    )

    dispatcher.add_handler(CallbackQueryHandler(result_mode_chosen, pattern=r'^(poem|line)$'))
    dispatcher.add_handler(CallbackQueryHandler(add_to_favorite_poems, pattern=r'^add\d{1,3}$'))
    dispatcher.add_handler(CallbackQueryHandler(remove_from_favorite_poems, pattern=r'^remove\d{1,3}$'))

    dispatcher.add_handler(InlineQueryHandler(handle_favorite_poems_inline_query, pattern=FAVORITE_POEMS_QUERY))
    dispatcher.add_handler(InlineQueryHandler(handle_inline_query))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

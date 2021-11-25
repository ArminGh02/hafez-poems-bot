from random import randrange
from re import compile
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

TOKEN = '<PLACE YOUR API TOKEN HERE>'
POEMS_DIRECTORY_NAME = 'divan/'
POEMS_COUNT = 495
FAVORITE_POEMS_QUERY = '#favorite_poems'
SURROUNDED_WITH_DOUBLE_QUOTES = r'"[\u0600-\u06FF\s]+"'
NO_MATCH_WAS_FOUND = 'هیچ بیتی با کلمات فرستاده شده پیدا نشد.'

user_to_favorite_poems: dict[User, set[str]] = {}
user_to_reply_with_line: dict[User, bool] = {}
to_invoke: Callable[[], None]


def get_poem(poem_number: int) -> str:
    poem_filename = POEMS_DIRECTORY_NAME + 'ghazal' + str(poem_number) + '.txt'
    with open(poem_filename, encoding='utf8') as poem:
        return poem.read()


def start(update: Update, context: CallbackContext) -> None:
    args = context.args
    if args and args[0] == 'inline-help':
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
            InlineKeyboardButton('Developer', 'https://telegram.me/ArminGh02')
        ]
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
        reply_markup=reply_markup
    )


def reply_line(update: Update, _: CallbackContext) -> None:
    user_to_reply_with_line[update.effective_user] = True
    update.message.reply_text('از این پس در نتیجه جستجو، بیت را دریافت خواهی کرد.✅')


def reply_ghazal(update: Update, _: CallbackContext) -> None:
    user_to_reply_with_line[update.effective_user] = False
    update.message.reply_text('از این پس در نتیجه جستجو، کل غزل را دریافت خواهی کرد.✅')


def random_poem_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(get_random_poem())


def get_random_poem() -> str:
    return get_poem(randrange(1, POEMS_COUNT))


def list_favorite_poems(update: Update, _: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton('لیست غزل های مورد علاقه ❤️', switch_inline_query_current_chat=FAVORITE_POEMS_QUERY)]
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
    def send_results() -> None:
        to_call = index_of_matched_line_string if isinstance(to_search, str) else index_of_matched_line_words
        results = find_results(update, to_search, to_call)
        if user_to_reply_with_line[update.effective_user]:
            for poem in results:
                update.message.reply_text(poem)
        else:
            for poem_number, poem in results:
                keyboard = [[InlineKeyboardButton('افزودن به غزل های مورد علاقه ❤️', callback_data=str(poem_number))]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text(poem, reply_markup=reply_markup)

    if update.effective_user not in user_to_reply_with_line:
        choose_result_mode(update)
        global to_invoke
        to_invoke = send_results
    else:
        send_results()


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


def find_results(update: Update,
                 to_search: Union[str, list[str]],
                 index_of_matched_line: Union[Callable[[list[str], str], int], Callable[[list[str], list[str]], int]]
                 ) -> list[str]:
    if update.effective_user not in user_to_reply_with_line:
        user_to_reply_with_line[update.effective_user] = True

    results = []
    found_match = False
    for i in range(1, POEMS_COUNT + 1):
        poem = get_poem(i)
        lines = poem.splitlines()
        j = index_of_matched_line(lines, to_search)
        if j > -1:
            found_match = True
            if user_to_reply_with_line[update.effective_user]:
                result = lines[j - 1] + '\n' + lines[j] + '\n' + lines[j + 1]
                results.append(result)
            else:
                results.append((i, poem))

    if not found_match:
        results.append(NO_MATCH_WAS_FOUND)

    return results


def choose_result_mode(update: Update) -> None:
    keyboard = [
        [InlineKeyboardButton('در نتیجه جستجو، کل غزل دریافت شود.', callback_data='ghazal')],
        [InlineKeyboardButton('در نتیجه جستجو، فقط بیت دریافت شود.', callback_data='line')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('لطفا انتخاب کن:', reply_markup=reply_markup)


def button_pressed(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    if query.data == 'line':
        user_to_reply_with_line[update.effective_user] = True
        query.edit_message_text(text='در نتیجه جستجو بیت دریافت می شود.')
        query.answer()
        to_invoke()
    elif query.data == 'ghazal':
        user_to_reply_with_line[update.effective_user] = False
        query.edit_message_text(text='در نتیجه جستجو کل غزل دریافت می شود.')
        query.answer()
        to_invoke()
    else:
        if update.effective_user not in user_to_favorite_poems:
            user_to_favorite_poems[update.effective_user] = {get_poem(int(query.data))}
        else:
            user_to_favorite_poems[update.effective_user].add(get_poem(int(query.data)))
        query.answer('این غزل به لیست علاقه مندی های شما افزوده شد.')


def handle_inline_query(update: Update, _: CallbackContext) -> None:
    query = update.inline_query.query
    user = update.effective_user

    favorite_poems_queried = query == FAVORITE_POEMS_QUERY
    persian_words = r'[\u0600-\u06FF\s]+'
    search_results = []
    if favorite_poems_queried:
        if user in user_to_favorite_poems:
            search_results = user_to_favorite_poems[user]
    elif compile(SURROUNDED_WITH_DOUBLE_QUOTES).match(query):
        search_results = find_results(update, query[1:-1], index_of_matched_line_string)
    elif compile(persian_words).match(query):
        search_results = find_results(update, query.split(), index_of_matched_line_words)

    results = []
    if not favorite_poems_queried:
        results.append(
            InlineQueryResultArticle(
                id=str(uuid4()),
                title='فال',
                input_message_content=InputTextMessageContent(get_random_poem())
            ),
        )
    if favorite_poems_queried or user_to_reply_with_line[user]:
        for search_result in search_results:
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=search_result[:40] + '...',
                    input_message_content=InputTextMessageContent(search_result),
                )
            )
    else:
        for _, search_result in search_results:
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=search_result[:40] + '...',
                    input_message_content=InputTextMessageContent(search_result),
                )
            )

    if favorite_poems_queried:
        update.inline_query.answer(results)
    else:
        update.inline_query.answer(results, switch_pm_text='راهنما ❓', switch_pm_parameter='inline-help')


def main() -> None:
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('fal', random_poem_command))
    dispatcher.add_handler(CommandHandler('ghazal', reply_ghazal))
    dispatcher.add_handler(CommandHandler('beit', reply_line))
    dispatcher.add_handler(CommandHandler('favorite', list_favorite_poems))
    dispatcher.add_handler(MessageHandler(Filters.regex(SURROUNDED_WITH_DOUBLE_QUOTES), search_string))
    dispatcher.add_handler(
        MessageHandler(
            Filters.text & ~Filters.command & ~Filters.via_bot(username='hafez_poems_bot'),
            search_words
        )
    )
    dispatcher.add_handler(CallbackQueryHandler(button_pressed))
    dispatcher.add_handler(InlineQueryHandler(handle_inline_query))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()

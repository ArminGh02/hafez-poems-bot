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

TOKEN = '<PLACE YOUR BOT API TOKEN HERE>'
POEMS_DIRECTORY_NAME = 'divan/'
POEMS_COUNT = 495
SURROUNDED_WITH_DOUBLE_QUOTES = r'"[\u0600-\u06FF\s]+"'
NO_MATCH_WAS_FOUND = 'هیچ بیتی با کلمات فرستاده شده پیدا نشد.'

reply_with_line: dict[User, bool] = {}
to_invoke: Callable[[], None]


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
        update.message.reply_text(
            f'سلام {update.effective_user.first_name}!\n'
            'با نوشتن چند کلمه از یک بیت حافظ، غزل یا بیتی را که \n'
            'یک بیتش شامل کلمات وارد شده، باشد دریافت خواهی کرد.\n'
            'در ضمن اگر می خواهی کل یک عبارت با هم (و نه تک تک کلماتش)\n'
            'در بیت جستجو شود، آن را درون "" بگذار.\n'
            'همچنین با زدن دستور /fal یک فال می توانی بگیری.\n'
        )


def reply_line(update: Update, _: CallbackContext) -> None:
    reply_with_line[update.effective_user] = True
    update.message.reply_text('از این پس در نتیجه جستجو، بیت را دریافت خواهی کرد.✅')


def reply_ghazal(update: Update, _: CallbackContext) -> None:
    reply_with_line[update.effective_user] = False
    update.message.reply_text('از این پس در نتیجه جستجو، کل غزل را دریافت خواهی کرد.✅')


def fal(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(find_fal())


def find_fal() -> str:
    rand = randrange(1, POEMS_COUNT)
    ghazal_filename = POEMS_DIRECTORY_NAME + 'ghazal' + str(rand) + '.txt'
    with open(ghazal_filename, encoding='utf8') as ghazal:
        return ghazal.read()


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
        for result in results:
            update.message.reply_text(result)

    if update.effective_user not in reply_with_line:
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
    if update.effective_user not in reply_with_line:
        reply_with_line[update.effective_user] = True

    results = []
    found_match = False
    for i in range(1, POEMS_COUNT + 1):
        ghazal_filename = POEMS_DIRECTORY_NAME + 'ghazal' + str(i) + '.txt'
        with open(ghazal_filename, encoding='utf8') as ghazal:
            ghazal_text = ghazal.read()
            lines = ghazal_text.splitlines()
            j = index_of_matched_line(lines, to_search)
            if j > -1:
                found_match = True
                if reply_with_line[update.effective_user]:
                    result = lines[j - 1] + '\n' + lines[j] + '\n' + lines[j + 1]
                    results.append(result)
                else:
                    results.append(ghazal_text)

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
    query.answer()
    text: str
    if query.data == 'line':
        text = 'در نتیجه جستجو بیت دریافت می شود.'
        reply_with_line[update.effective_user] = True
    else:
        text = 'در نتیجه جستجو کل غزل دریافت می شود.'
        reply_with_line[update.effective_user] = False
    query.edit_message_text(text=text)
    to_invoke()


def handle_inline_query(update: Update, _: CallbackContext) -> None:
    query = update.inline_query.query

    persian_words = r'[\u0600-\u06FF\s]+'
    search_results = []
    if compile(SURROUNDED_WITH_DOUBLE_QUOTES).match(query):
        search_results = find_results(update, query[1:-1], index_of_matched_line_string)
    elif compile(persian_words).match(query):
        search_results = find_results(update, query.split(), index_of_matched_line_words)

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title='فال',
            input_message_content=InputTextMessageContent(find_fal())
        ),
    ]
    for search_result in search_results:
        results.append(
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=search_result[:40] + '...',
                input_message_content=InputTextMessageContent(search_result)
            )
        )

    update.inline_query.answer(results, switch_pm_text='راهنما ❓', switch_pm_parameter='inline-help')


def main() -> None:
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('fal', fal))
    dispatcher.add_handler(CommandHandler('ghazal', reply_ghazal))
    dispatcher.add_handler(CommandHandler('beit', reply_line))
    dispatcher.add_handler(MessageHandler(Filters.regex(SURROUNDED_WITH_DOUBLE_QUOTES), search_string))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, search_words))
    dispatcher.add_handler(CallbackQueryHandler(button_pressed))
    dispatcher.add_handler(InlineQueryHandler(handle_inline_query))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()

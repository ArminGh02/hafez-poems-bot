from random import randrange
from typing import (
    Callable,
    Union
)

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    User
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater
)

TOKEN = '<PLACE YOUR BOT API TOKEN HERE>'
POEMS_DIRECTORY_NAME = 'divan/'
GHAZALS_COUNT = 495
SURROUNDED_WITH_DOUBLE_QUOTES = r'"[\u0600-\u06FF\s]+"'
NO_MATCH_WAS_FOUND = 'هیچ بیتی با کلمات فرستاده شده پیدا نشد.'

reply_with_line: dict[User, bool] = {}
to_invoke: Callable[[], None]


def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(f'سلام {update.effective_user.first_name}!\n'
                              'با نوشتن چند کلمه از یک بیت حافظ، غزلی را که \n'
                              'یک بیتش شامل کلمات وارد شده، باشد دریافت خواهی کرد.\n'
                              'در ضمن اگر می خواهی کل یک عبارت در بیت جستجو \n'
                              'شود، آن را درون "" بگذار.\n'
                              'همچنین با زدن دستور /fal یک فال می توانی بگیری.\n')


def reply_line(update: Update, _: CallbackContext) -> None:
    reply_with_line[update.effective_user] = True
    update.message.reply_text('از این پس در نتیجه جستجو، بیت را دریافت خواهی کرد.✅')


def reply_ghazal(update: Update, _: CallbackContext) -> None:
    reply_with_line[update.effective_user] = False
    update.message.reply_text('از این پس در نتیجه جستجو، کل غزل را دریافت خواهی کرد.✅')


def fal(update: Update, _: CallbackContext) -> None:
    rand = randrange(1, GHAZALS_COUNT)
    ghazal_filename = POEMS_DIRECTORY_NAME + 'ghazal' + str(rand) + '.txt'
    with open(ghazal_filename, encoding='utf8') as ghazal:
        update.message.reply_text(ghazal.read())


def search_words(update: Update, _: CallbackContext) -> None:
    def index_of_matched_line(lines: list[str], words_to_search: list[str]) -> int:
        for i, line in enumerate(lines):
            if all(word in line for word in words_to_search):
                return i
        return -1

    words = update.message.text.split()
    search(update, words, index_of_matched_line)


def search_string(update: Update, _: CallbackContext) -> None:
    def index_of_matched_line(lines: list[str], to_search: str) -> int:
        for i, line in enumerate(lines):
            if to_search in line:
                return i
        return -1

    string_to_search = update.message.text[1:-1]  # remove "" (double quotes) from start and end of string
    search(update, string_to_search, index_of_matched_line)


def search(update: Update,
           to_search: Union[str, list[str]],
           index_of_matched_line: Union[Callable[[list[str], str], int], Callable[[list[str], list[str]], int]]
           ) -> None:
    def rest() -> None:
        found_match = False
        for i in range(1, GHAZALS_COUNT + 1):
            ghazal_filename = POEMS_DIRECTORY_NAME + 'ghazal' + str(i) + '.txt'
            with open(ghazal_filename, encoding='utf8') as ghazal:
                ghazal_text = ghazal.read()
                lines = ghazal_text.splitlines()
                j = index_of_matched_line(lines, to_search)
                if j > -1:
                    found_match = True
                    if reply_with_line[update.effective_user]:
                        result = lines[j - 1] + '\n' + lines[j] + '\n' + lines[j + 1]
                        update.message.reply_text(result)
                    else:
                        update.message.reply_text(ghazal_text)

        if not found_match:
            update.message.reply_text(NO_MATCH_WAS_FOUND)

    if update.effective_user not in reply_with_line:
        choose_result_mode(update)
        global to_invoke
        to_invoke = rest
    else:
        rest()


def choose_result_mode(update: Update):
    keyboard = [
        [InlineKeyboardButton('در نتیجه جستجو، کل غزل دریافت شود.', callback_data='ghazal')],
        [InlineKeyboardButton('در نتیجه جستجو، فقط بیت دریافت شود.', callback_data='line')]
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


def main() -> None:
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('fal', fal))
    updater.dispatcher.add_handler(CommandHandler('ghazal', reply_ghazal))
    updater.dispatcher.add_handler(CommandHandler('beit', reply_line))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(SURROUNDED_WITH_DOUBLE_QUOTES), search_string))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, search_words))
    updater.dispatcher.add_handler(CallbackQueryHandler(button_pressed))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()

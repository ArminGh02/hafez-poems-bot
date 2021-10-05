import random
from typing import (
    Callable,
    Union
)

from telegram import (
    Update,
    User
)
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    Filters
)

TOKEN = '<PLACE YOUR BOT API TOKEN HERE>'
POEMS_DIRECTORY_NAME = 'divan/'
GHAZALS_COUNT = 495
SURROUNDED_WITH_DOUBLE_QUOTES = r'"[\u0600-\u06FF\s]+"'
NO_MATCH_WAS_FOUND = 'هیچ بیتی با کلمات فرستاده شده پیدا نشد.'

reply_with_line: dict[User, bool] = {}


def start(update: Update, context: CallbackContext) -> None:
    reply_with_line[update.effective_user] = True
    update.message.reply_text(f'سلام {update.effective_user.first_name}!\n'
                              'با نوشتن چند کلمه از یک بیت حافظ، غزلی را که \n'
                              'یک بیتش شامل کلمات وارد شده، باشد دریافت خواهی کرد.\n'
                              'در ضمن اگر می خواهی کل یک عبارت در بیت جستجو \n'
                              'شود، آن را درون "" بگذار.\n'
                              'همچنین با زدن دستور /fal یک فال می توانی بگیری.\n')


def reply_line(update: Update, context: CallbackContext) -> None:
    reply_with_line[update.effective_user] = True
    update.message.reply_text('از این پس در نتیجه جستجو، بیت را دریافت خواهی کرد.✅')


def reply_ghazal(update: Update, context: CallbackContext) -> None:
    reply_with_line[update.effective_user] = False
    update.message.reply_text('از این پس در نتیجه جستجو، کل غزل را دریافت خواهی کرد.✅')


def fal(update: Update, context: CallbackContext) -> None:
    rand = random.randrange(1, GHAZALS_COUNT)
    ghazal_filename = POEMS_DIRECTORY_NAME + 'ghazal' + str(rand) + '.txt'
    with open(ghazal_filename, encoding='utf8') as ghazal:
        update.message.reply_text(ghazal.read())


def search_words(update: Update, context: CallbackContext) -> None:
    def index_of_matched_line(lines: list[str], words_to_search: list[str]) -> int:
        for i, line in enumerate(lines):
            if all(word in line for word in words_to_search):
                return i
        return -1

    words = update.message.text.split()
    search(update, words, index_of_matched_line)


def search_string(update: Update, context: CallbackContext) -> None:
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
    if update.effective_user not in reply_with_line:
        reply_with_line[update.effective_user] = True

    found_match = False
    for i in range(1, GHAZALS_COUNT + 1):
        ghazal_filename = POEMS_DIRECTORY_NAME + 'ghazal' + str(i) + '.txt'
        with open(ghazal_filename, encoding='utf8') as ghazal:
            ghazal_text = ghazal.read()
            lines = ghazal_text.splitlines()
            j = index_of_matched_line(lines, to_search)
            if j > -1:
                found_match = True
                update.message.reply_text(lines[j] if reply_with_line[update.effective_user] else ghazal_text)

    if not found_match:
        update.message.reply_text(NO_MATCH_WAS_FOUND)


def main():
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('fal', fal))
    updater.dispatcher.add_handler(CommandHandler('ghazal', reply_ghazal))
    updater.dispatcher.add_handler(CommandHandler('beit', reply_line))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(SURROUNDED_WITH_DOUBLE_QUOTES), search_string))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, search_words))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()

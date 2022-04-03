from telegram import (
    Update,
)
from telegram.ext import (
    CallbackContext,
)

import config
import helper


def search_words(update: Update, _: CallbackContext) -> None:
    query = helper.make_yeh_arabic(update.message.text)

    if config.db.is_reply_with_line(update.effective_user.id) is None:
        helper.choose_result_mode(update, query)
        return

    helper.search_impl(update, query.split())


def search_string(update: Update, _: CallbackContext) -> None:
    query = helper.make_yeh_arabic(update.message.text)

    if config.db.is_reply_with_line(update.effective_user.id) is None:
        helper.choose_result_mode(update, query)
        return

    helper.search_impl(update, query[1:-1])

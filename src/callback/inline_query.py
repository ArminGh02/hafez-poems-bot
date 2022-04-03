import re
from uuid import uuid4

from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
)
from telegram.ext import (
    CallbackContext,
)

import config
import helper


def handle_favorite_poems(update: Update, _: CallbackContext) -> None:
    user = update.effective_user
    favorite_poems = map(lambda poem_index: config.poems[poem_index], config.db.get_favorite_poems(user.id))

    if not favorite_poems:
        update.inline_query.answer(
            results=[],
            cache_time=0,
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
                reply_markup=helper.build_poem_keyboard(poem, user, True),
            ),
            favorite_poems,
        )
    )
    update.inline_query.answer(results, cache_time=0, auto_pagination=True)


def handle(update: Update, _: CallbackContext) -> None:
    query = helper.make_yeh_arabic(update.inline_query.query)
    user = update.effective_user

    search_results = []
    if config.SURROUNDED_WITH_DOUBLE_QUOTES.match(query):
        search_results = helper.find_results(update, query[1:-1])
    elif config.PERSIAN_WORDS.match(query):
        search_results = helper.find_results(update, query.split())

    random_poem = helper.get_random_poem()
    random_poem_article = InlineQueryResultArticle(
        id=str(uuid4()),
        title='فال 🎲',
        input_message_content=InputTextMessageContent(random_poem.text),
        reply_markup=helper.build_poem_keyboard(random_poem, user, True),
    )

    if not search_results:
        update.inline_query.answer(
            results=[random_poem_article],
            cache_time=0,
            switch_pm_text=config.NO_MATCH_WAS_FOUND,
            switch_pm_parameter=config.INLINE_HELP,
        )
        return

    if config.db.is_reply_with_line(user.id, True):
        results = [
            random_poem_article,
            *map(
                lambda search_result: InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=search_result,
                    input_message_content=InputTextMessageContent(search_result),
                ),
                search_results,
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
                    reply_markup=helper.build_poem_keyboard(poem, user, True),
                ),
                search_results,
            ),
        ]

    update.inline_query.answer(
        results,
        cache_time=0,
        switch_pm_text='راهنما ❓',
        switch_pm_parameter=config.INLINE_HELP,
        auto_pagination=True,
    )

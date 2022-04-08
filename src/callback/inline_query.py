from typing import Union
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
from poem import Poem
from search import Searcher


def favorite_poems(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    fav_poems = map(lambda poem_index: config.poems[poem_index], config.db.favorite_poems(user.id))

    if not fav_poems:
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
                reply_markup=helper.build_poem_keyboard(poem, user, context.bot.username, True),
            ),
            fav_poems,
        )
    )
    update.inline_query.answer(results, cache_time=0, auto_pagination=True)


def handle(update: Update, context: CallbackContext) -> None:
    query = helper.make_yeh_arabic(update.inline_query.query)
    user = update.effective_user

    search_results = []
    if config.SURROUNDED_WITH_DOUBLE_QUOTES.match(query):
        search_results = Searcher.matching_poems_and_lines(query[1:-1])
    elif config.PERSIAN_WORDS.match(query):
        search_results = Searcher.matching_poems_and_lines(query.split())

    rand_poem = helper.random_poem()
    random_poem_article = InlineQueryResultArticle(
        id=str(uuid4()),
        title='فال 🎲',
        input_message_content=InputTextMessageContent(rand_poem.text),
        reply_markup=helper.build_poem_keyboard(rand_poem, user, context.bot.username, True),
    )

    if not search_results:
        update.inline_query.answer(
            results=[random_poem_article],
            cache_time=0,
            switch_pm_text=config.NO_MATCH_WAS_FOUND,
            switch_pm_parameter=config.INLINE_HELP,
        )
        return

    def result_to_article(search_res: Union[str, Poem]) -> InlineQueryResultArticle:
        if isinstance(search_res, str):
            return InlineQueryResultArticle(
                id=str(uuid4()),
                title='بیت: ' + search_res,
                input_message_content=InputTextMessageContent(search_res),
            )
        if isinstance(search_res, Poem):
            return InlineQueryResultArticle(
                id=str(uuid4()),
                title='غزل: ' + search_res.text,
                input_message_content=InputTextMessageContent(
                    search_res.text + '🎼وزن: ' + search_res.meter
                ),
                reply_markup=helper.build_poem_keyboard(search_res, user, context.bot.username, True),
            )
        raise TypeError(f'unsupported type: {type(search_res)}')

    update.inline_query.answer(
        results=[random_poem_article, *map(result_to_article, search_results)],
        cache_time=0,
        switch_pm_text='راهنما ❓',
        switch_pm_parameter=config.INLINE_HELP,
        auto_pagination=True,
    )

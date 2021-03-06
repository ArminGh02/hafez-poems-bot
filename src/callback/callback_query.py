from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    CallbackContext,
)

import config
import helper


def result_mode_chosen(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    query = update.callback_query
    data = query.data

    if data.startswith('line_'):
        text = 'در نتیجه جستجو بیت دریافت می شود.'
        config.db.set_reply_with_line(user.id, True)
        search_query = data.removeprefix('line_')
    else:  # data == 'poem_<query>'
        text = 'در نتیجه جستجو کل غزل دریافت می شود.'
        config.db.set_reply_with_line(user.id, False)
        search_query = data.removeprefix('poem_')

    query.edit_message_text(text)
    query.answer()

    if search_query.startswith('"'):
        helper.search_impl(update, search_query[1:-1], context.bot.username)
    else:
        helper.search_impl(update, search_query.split(), context.bot.username)


def add_to_favorite_poems(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    query = update.callback_query

    poem_index = int(query.data.removeprefix('add'))

    config.db.add_to_favorite_poems(user.id, poem_index)

    reply_markup = helper.build_poem_keyboard(
        config.poems[poem_index],
        user,
        context.bot.username,
        update.effective_chat is None,
    )
    query.edit_message_reply_markup(reply_markup)
    query.answer('این غزل به لیست علاقه‌مندی‌های شما افزوده شد.')


def remove_from_favorite_poems(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    query = update.callback_query

    poem_index = int(query.data.removeprefix('remove'))

    config.db.remove_from_favorite_poems(user.id, poem_index)

    reply_markup = helper.build_poem_keyboard(
        config.poems[poem_index],
        user,
        context.bot.username,
        update.effective_chat is None,
    )
    query.edit_message_reply_markup(reply_markup)
    query.answer('این غزل از لیست علاقه‌مندی‌های شما حذف شد.')


def send_audio_of_poem(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    poem_index = int(query.data.removeprefix('audio'))

    context.bot.forward_message(
        chat_id=update.effective_chat.id,
        from_chat_id=config.DATABASE_CHANNEL_USERNAME,
        message_id=poem_index + 2,   # channel message ID's start from 2
    )

    query.answer()


def display_related_songs(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    poem_index = int(query.data.removeprefix('songs'))

    keyboard = [
        *map(
            lambda song: [InlineKeyboardButton(song.title, url=song.link)],
            config.poems[poem_index].related_songs,
        ),
        [InlineKeyboardButton('بازگشت 🔙', callback_data=f'back{poem_index}')]
    ]

    query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))
    query.answer()


def return_to_menu_of_poem(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    poem_index = int(query.data.removeprefix('back'))
    user = update.effective_user

    reply_markup = helper.build_poem_keyboard(
        config.poems[poem_index],
        user,
        context.bot.username,
        update.effective_chat is None,
    )
    query.edit_message_reply_markup(reply_markup)
    query.answer()

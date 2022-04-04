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


def start(update: Update, context: CallbackContext) -> None:
    args = context.args
    if args:
        if args[0] == config.INLINE_HELP:
            update.message.reply_text(
                'بعد از نوشتن یوزرنیمِ بات در یک چت،\n'
                'با نوشتن چند کلمه از یک بیت حافظ، غزل یا بیتی را که\n'
                'یک بیتش شامل کلمات وارد شده، باشد دریافت خواهی کرد.\n'
                'در ضمن اگر می خواهی کل یک عبارت با هم (و نه تک تک کلماتش)\n'
                'در بیت جستجو شود، آن را درون "" بگذار.'
            )
        elif args[0].startswith(config.SEND_AUDIO):
            poem_index = int(args[0].removeprefix(config.SEND_AUDIO))
            context.bot.forward_message(
                chat_id=update.effective_chat.id,
                from_chat_id=config.DATABASE_CHANNEL_USERNAME,
                message_id=poem_index + 2   # channel message ID's start from 2
            )
    else:
        help_(update, context)
        config.db.add_user(update.effective_user.id)


def help_(update: Update, _: CallbackContext) -> None:
    text = (f'سلام {update.effective_user.first_name}!\n'
        'با نوشتن چند کلمه از یک بیت حافظ، غزل یا بیتی را که \n'
        'یک بیتش شامل کلمات وارد شده، باشد دریافت خواهی کرد.\n'
        'در ضمن اگر می خواهی کل یک عبارت با هم (و نه تک تک کلماتش)\n'
        'در بیت جستجو شود، آن را درون "" بگذار.\n'
        'همچنین با زدن دستور /faal یک فال می توانی بگیری.\n'
        f'تعداد کاربران: {config.db.users_count()}')
    keyboard = [
        [
            InlineKeyboardButton('Github', config.GITHUB_REPO),
            InlineKeyboardButton('Developer', config.DEVELOPER_USERNAME),
        ],
    ]
    update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


def reply_line(update: Update, _: CallbackContext) -> None:
    config.db.set_reply_with_line(update.effective_user.id, True)
    update.message.reply_text('از این پس در نتیجه جستجو، بیت را دریافت خواهی کرد.✅')


def reply_poem(update: Update, _: CallbackContext) -> None:
    config.db.set_reply_with_line(update.effective_user.id, False)
    update.message.reply_text('از این پس در نتیجه جستجو، کل غزل را دریافت خواهی کرد.✅')


def random_poem(update: Update, context: CallbackContext) -> None:
    poem = helper.get_random_poem()
    update.message.reply_text(
        text=poem.text + '🎼وزن: ' + poem.meter,
        reply_markup=helper.build_poem_keyboard(poem, update.effective_user, context.bot.username, False),
    )


def list_favorite_poems(update: Update, _: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton(
                'لیست غزل های مورد علاقه ❤️',
                switch_inline_query_current_chat=config.FAVORITE_POEMS_QUERY
            )
        ],
    ]
    update.message.reply_text(
        text='دکمه زیر را بزن.',
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    InlineQueryHandler,
    MessageHandler,
    Updater,
)

import config
from callback import (
    callback_query,
    command,
    inline_query,
    message,
)


def main() -> None:
    updater = Updater(config.API_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', command.start))
    dispatcher.add_handler(CommandHandler('help', command.help_))
    dispatcher.add_handler(CommandHandler('faal', command.random_poem))
    dispatcher.add_handler(CommandHandler('favorite', command.list_favorite_poems))
    dispatcher.add_handler(CommandHandler('ghazal', command.reply_poem))
    dispatcher.add_handler(CommandHandler('beit', command.reply_line))

    dispatcher.add_handler(
        MessageHandler(
            Filters.regex(config.SURROUNDED_WITH_DOUBLE_QUOTES),
            message.search_string
        )
    )
    dispatcher.add_handler(
        MessageHandler(
            Filters.regex(config.PERSIAN_WORDS) & ~Filters.via_bot(username=updater.bot.username),
            message.search_words,
        )
    )

    dispatcher.add_handler(CallbackQueryHandler(callback_query.result_mode_chosen, pattern=r'^(poem_|line_)'))
    dispatcher.add_handler(CallbackQueryHandler(callback_query.add_to_favorite_poems, pattern=r'^add\d{1,3}$'))
    dispatcher.add_handler(CallbackQueryHandler(callback_query.remove_from_favorite_poems, pattern=r'^remove\d{1,3}$'))
    dispatcher.add_handler(CallbackQueryHandler(callback_query.send_audio_of_poem, pattern=r'^audio\d{1,3}$'))
    dispatcher.add_handler(CallbackQueryHandler(callback_query.display_related_songs, pattern=r'^songs\d{1,3}$'))
    dispatcher.add_handler(CallbackQueryHandler(callback_query.return_to_menu_of_poem, pattern=r'^back\d{1,3}$'))

    dispatcher.add_handler(InlineQueryHandler(inline_query.favorite_poems, pattern=config.FAVORITE_POEMS_QUERY))
    dispatcher.add_handler(InlineQueryHandler(inline_query.handle))

    updater.bot.set_my_commands(
        [
            ('start', 'بات را ری‌استارت می‌کند'),
            ('help', 'راهنما'),
            ('faal', 'یک فال حافظ می‌گیرد'),
            ('favorite', 'لیست غزل های مورد علاقه را نشان می‌دهد'),
            ('ghazal', 'در نتیجه جستجو کل غزل را می‌فرستد'),
            ('beit', 'در نتیجه جستجو فقط بیت را می‌فرستد'),
        ]
    )

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

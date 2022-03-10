import json

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    InlineQueryHandler,
    MessageHandler,
    Updater,
)

import consts
from callback import (
    callback_query,
    command,
    inline_query,
    message,
)
from poem import (
    Poem,
    Song,
)


def _init_poems() -> None:
    poems_list = [None] * consts.POEMS_COUNT
    for i in range(consts.POEMS_COUNT):
        with open(f'divan/ghazal{i + 1}.txt', encoding='utf8') as poem_file:
            text = poem_file.read()
        with open(f'data/poem_{i + 1}_info.json', encoding='utf8') as json_file:
            poem_info = json.load(json_file)
        meter = poem_info['meter']
        related_songs = tuple(
            map(
                lambda song: Song(song['title'], song['link']),
                poem_info['relatedSongs'],
            )
        )
        poems_list[i] = Poem(meter, i, related_songs, text)

    consts.poems = tuple(poems_list)


def main() -> None:
    _init_poems()

    updater = Updater(consts.API_TOKEN)
    dispatcher = updater.dispatcher
    bot = updater.bot

    consts.BOT_USERNAME = bot.username

    dispatcher.add_handler(CommandHandler('start', command.start))
    dispatcher.add_handler(CommandHandler('help', command.help_command))
    dispatcher.add_handler(CommandHandler('faal', command.random_poem_command))
    dispatcher.add_handler(CommandHandler('favorite', command.list_favorite_poems))
    dispatcher.add_handler(CommandHandler('ghazal', command.reply_poem))
    dispatcher.add_handler(CommandHandler('beit', command.reply_line))

    dispatcher.add_handler(
        MessageHandler(
            Filters.regex(consts.SURROUNDED_WITH_DOUBLE_QUOTES),
            message.search_string
        )
    )
    dispatcher.add_handler(
        MessageHandler(
            Filters.text & ~Filters.command & ~Filters.via_bot(username=consts.BOT_USERNAME),
            message.search_words,
        )
    )

    dispatcher.add_handler(CallbackQueryHandler(callback_query.result_mode_chosen, pattern=r'^(poem_|line_)'))
    dispatcher.add_handler(CallbackQueryHandler(callback_query.add_to_favorite_poems, pattern=r'^add\d{1,3}$'))
    dispatcher.add_handler(CallbackQueryHandler(callback_query.remove_from_favorite_poems, pattern=r'^remove\d{1,3}$'))
    dispatcher.add_handler(CallbackQueryHandler(callback_query.send_audio_of_poem, pattern=r'^audio\d{1,3}$'))
    dispatcher.add_handler(CallbackQueryHandler(callback_query.display_related_songs, pattern=r'^songs\d{1,3}$'))
    dispatcher.add_handler(CallbackQueryHandler(callback_query.return_to_menu_of_poem, pattern=r'^back\d{1,3}$'))

    dispatcher.add_handler(InlineQueryHandler(inline_query.handle_favorite_poems, pattern=consts.FAVORITE_POEMS_QUERY))
    dispatcher.add_handler(InlineQueryHandler(inline_query.handle))

    bot.set_my_commands(
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

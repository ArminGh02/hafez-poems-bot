
# Hafez Poems Telegram Bot

- [About](#about)
- [Web Scraping](#web-scraping)
- [Features](#features)
  - [Search for Poems](#search-for-poems)
  - [Get a Random Poem](#get-a-random-poem)
  - [Inline Mode](#inline-mode)
  - [Recitation of Each Poem](#recitation-of-each-poem)
  - [Related Songs](#related-songs)
  - [Poem Meters](#poem-meters)

## About
This is a simple Telegram Bot made mostly for learning purposes.
It is written in Python using **[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)** library. You can find it in Telegram via **[this link](https://t.me/hafez_poems_bot)**.

## Web Scraping
With the help of **[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)** (Python HTML parser library), I scraped **[Ganjoor](ganjoor.net)** to get recitations, poem meters and link of related songs.
The code I used for this purpose can be found **[here](ganjoor_scraping)**.

## Features

### Search for Poems
The bot enables you to search in all **[Hafez](https://en.wikipedia.org/wiki/Hafez)** poems in two ways:
- Search for one line of poem that consists of all words of query
- Search for certain words that appeared in one line of poem in the specified order and consecutively

First one is done by simply entering the desired words in any order.

And the second is done by surrounding your words with double quotes. (In both ways, the bot acts similar to what Google does.)

The result of your search can be set (via commands) to either return the whole poem or only the matching line.

### Get a Random Poem
There is a command to get a random poem.

### Inline Mode
The bot also supports inline queries. Meaning that you can type bot username in every telegram chat and then search for a query.

### Recitation of Each Poem
Thanks to **[Ganjoor](ganjoor.net)**, for each poem, you can receive an audio file containig recitation of the poem.

### Related Songs
Thanks to **[Ganjoor](ganjoor.net)**, for each poem there is a list of songs that used that poem.

### Poem Meters
You receive each poem with its meter appended.

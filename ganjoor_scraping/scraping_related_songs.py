from scraping_poems_meters import get_response

import json
from typing import Any

from bs4 import BeautifulSoup


def main() -> None:
    poems_info: list[dict[str, Any]] = []
    for i in range(1, 496):
        with open(f'data/poem_{i}_info.json', encoding='utf8') as json_file:
            poem_info = json.load(json_file)
        poems_info.append(poem_info)

    for i in range(1, 496):
        response = get_response(i)

        soup = BeautifulSoup(response.text, 'html.parser')
        related_songs_a_tags = [div.find('a') for div in soup.find_all('div', {'class': 'related-song'})]
        poems_info[i - 1]['relatedSongs'] = [{'title': tag.text, 'link': tag['href']} for tag in related_songs_a_tags]

        print('%d-' % i, poems_info[i - 1])

        with open(f'data/poem_{i}_info.json', 'w', encoding='utf8') as out:
            json.dump(poems_info[i - 1], out, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()

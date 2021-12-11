import requests
from requests.models import Response
import json
import os

from bs4 import BeautifulSoup


url = 'https://ganjoor.net/hafez/ghazal/sh{:d}/'
out_dir = 'data'


def get_response(poem_number: int) -> Response:
    while True:
        try:
            response = requests.get(url.format(poem_number))
        except:
            print('Unable to connect to ganjoor.net, poem_number =', poem_number)
            continue

        if response.status_code != 200:
            print(f'Unable to connect to ganjoor.net. Status code={response.status_code}, poem_number={poem_number}')
            continue

        return response


def main() -> None:
    if not os.path.exists(out_dir) or not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    for i in range(1, 496):
        response = get_response(i)

        soup = BeautifulSoup(response.text, 'html.parser')
        td_tags = soup.find_all('td')
        tag = iter(td_tags)
        current = next(tag, None)
        for next_ in tag:
            if 'وزن' in current.text:
                with open(out_dir + f'/poem_{i}_info.json', 'w', encoding='utf8') as out:
                    json.dump({'meter': next_.text.strip()}, out, indent=4, ensure_ascii=False)
                break
            current = next_


if __name__ == '__main__':
    main()

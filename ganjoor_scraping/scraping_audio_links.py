from scraping_poems_meters import get_response

from bs4 import BeautifulSoup


def main() -> None:
    urls = []
    for i in range(1, 495):
        response = get_response(i)

        soup = BeautifulSoup(response.text, 'html.parser')
        audio_tag = soup.find('audio', id='audio-1')
        source = audio_tag.find('source')

        urls.append(source['src'])
        print('%d- ' % i, urls[i - 1])

    with open('audio-urls.txt', 'w') as out:
        out.write('\n'.join(urls))
        out.flush()


if __name__ == '__main__':
    main()

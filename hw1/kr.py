import re
import urllib.request


def find_info(link):
    topic = re.compile('Категория: .*?>(.*?)</a>')
    time = re.compile('от <a href=.*?>(.*?)</a>')
    author = re.compile('Автор: <a.*?>(.*?)</a>')
    text = re.compile('<div id="article">(.*?)</div>', flags=re.DOTALL)

    reg_tag = re.compile('<.*?>', re.DOTALL)
    reg_space = re.compile('\s{2,}', re.DOTALL)

    req = urllib.request.Request(link)
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')

        article_topic = re.findall(topic, html)[0]
        article_time = re.findall(time, html)[0]
        article_author = re.findall(author, html)[0]
        article_text = re.findall(text, html)[0]

        clean_article_text = reg_tag.sub(" ", article_text)
        clean_article_text = reg_space.sub(" ", clean_article_text)

        return {
            'topic': article_topic,
            'time': article_time,
            'author': article_author,
            'text': clean_article_text
        }


def load_links(page_number):
    header = re.compile('<header><h3>(.*?)</h3>')

    link = re.compile('<a href="(.*?)"')

    title = re.compile('>(.*?)</a>')

    articles = []

    req = urllib.request.Request('http://www.kr74.ru/lastnews/page/' + str(page_number) + '/')
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')

        m = re.findall(header, html)
        for news in m:
            article_link = re.findall(link, news)[0]
            article_header = re.findall(title, news)[0]
            article = {
                'title': article_header,
                'link': article_link
            }
            articles.append(article)

    return articles


def main():
    articles = load_links(2)
    for article in articles:
        article.update(find_info(article['link']))

        print('Ссылка: {}\nАвтор: {}\nЗаголовок: {}\nКатегория: {}\nВремя: {}\n\nТекст: {}\n\n\n'.format(
            article['link'],
            article['author'],
            article['title'],
            article['topic'],
            article['time'],
            article['text']))


if __name__ == '__main__':
    main()
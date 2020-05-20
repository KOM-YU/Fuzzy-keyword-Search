"""
爬取一个读后感网站上的读后感，用作文档集合
"""

import requests
from bs4 import BeautifulSoup


def gethtml(url):
    try:
        r = requests.get(url, timeout = 30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return '发生异常'


def get_title(text):
    soup = BeautifulSoup(text, 'html.parser')
    title_list = soup.find_all('h1')
    title = title_list[0].string
    return  title


def get_content(text):
    soup = BeautifulSoup(text, 'html.parser')
    content = str(soup.p.text).replace(chr(12288), '')
    return content


if __name__ == "__main__":
       for i in range(1101, 1601):
            url = 'https://www.duhougan.net/article-{}.html'.format(i)
            html = gethtml(url)
            title = get_title(html)
            content = get_content(html)
            path = 'D:\\Fuzzy Keywords Search\\测试文件夹\\500\\{}.txt'.format(title)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
import re
import logging
from urllib.parse import urljoin
import json

import jsbeautifier

from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class Qiman6Crawler(CrawlerBase):

    SITE = "qiman6"
    SITE_INDEX = 'http://www.qiman6.com/'
    SOURCE_NAME = "奇漫屋"
    LOGIN_URL = SITE_INDEX

    DEFAULT_COMICID = '16041'
    DEFAULT_SEARCH_NAME = '和'
    DEFAULT_TAG = "1"
    COMICID_PATTERN = re.compile(r'/(\d+)/?')

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, "/{}/".format(comicid))

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        name = soup.h1.text
        author = ''
        tag = ''
        status = ''
        for span in soup.find('div', {'class': 'ib info'}).find_all('span'):
            if '作  者：' in span.text:
                author = span.text.replace('作  者：', '').strip()
            elif '类  别：' in span.text:
                tag = span.text.replace('类  别：', '').strip()
            elif '状  态：' in span.text:
                status = span.text.replace('状  态：', '').strip()

        desc = soup.find('p', {'class': 'content'}).text.strip()
        cover_image_url = soup.find('div', {'class', 'img'}).img.get('src')
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       status=status,
                                       source_url=self.source_url)
        book.add_tag(name=tag, tag=tag)

        api = "http://www.qiman6.com/bookchapter/"
        params = {'id': self.comicid, 'id2': 1}
        response = self.send_request('POST', api, data=params)
        api_data = response.json()
        current = 1
        for chapter_number, item in enumerate(reversed(api_data), start=1):
            chapterid = item['chapterid']
            url = urljoin(self.SITE_INDEX, '/{}/{}.html'.format(self.comicid, chapterid))
            title = item['chaptername']
            book.add_chapter(chapter_number=chapter_number,
                             source_url=url,
                             title=title)
            current += 1

        li_list = soup.find('div', {'id': 'chapter-list1'}).find_all('a', recursive=False)
        for chapter_number, a in enumerate(reversed(li_list), start=current):
            href = a.get('href')
            url = urljoin(self.SITE_INDEX, href)
            title = a.text.strip()
            book.add_chapter(chapter_number=chapter_number,
                             source_url=url,
                             title=title)

        return book

    def get_chapter_image_urls(self, citem):
        html = self.get_html(citem.source_url)
        s = re.search(r'<script type="text/javascript">\s+(eval.*?)</script>', html, re.S).group(1).strip()
        js_str = jsbeautifier.beautify(s)
        re.search('var newImgs = (.*?)', js_str)
        image_urls = json.loads(re.search(r'var newImgs = (\[.*\])', js_str).group(1))
        return image_urls

    def latest(self, page=1):
        url = urljoin(self.SITE_INDEX, "/rank/5-%s.html" % page)
        soup = self.get_soup(url)
        return self.parse_book_list(soup)

    def parse_book_list(self, soup):
        result = self.new_search_result_item()
        for div in soup.find('div', {'class': 'bookList_3'}).find_all('div', recursive=False):
            href = div.a.get('href')
            comicid = self.get_comicid_by_url(href)
            source_url = urljoin(self.SITE_INDEX, href)
            name = div.find('p', {'class': 'title'}).text.strip()
            cover_image_url = div.find('img', {'class': 'cover'}).get('src')
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def get_tags(self):
        tags = self.new_tags_item()
        for name, tag_id in [
            ('冒险热血', 1),
            ('武侠格斗', 2),
            ('科幻魔幻', 3),
            ('侦探推理', 4),
            ('耽美爱情', 5),
            ('生活漫画', 6),
            ('完结漫画', 12),
            ('连载漫画', 13),
        ]:
            category = '分类'
            tags.add_tag(category=category, name=name, tag=tag_id)
        return tags

    def get_tag_result(self, tag, page=1):
        if not tag:
            tag = 1
        url = urljoin(self.SITE_INDEX, "/sort/%s-%s.html" % (tag, page))
        soup = self.get_soup(url)
        return self.parse_book_list(soup)

    def search(self, name, page=1, size=None):
        if page > 1:
            return self.new_search_result_item()
        url = urljoin(self.SITE_INDEX, "/search.php?keyword=%s" % name)
        soup = self.get_soup(url)
        return self.parse_book_list(soup)

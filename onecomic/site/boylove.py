import re
import logging
import json
import html
from urllib.parse import urljoin

from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class BoyloveCrawler(CrawlerBase):

    SITE = "boylove"
    SITE_INDEX = 'https://boylove.cc/'
    SOURCE_NAME = "BoyLove"
    LOGIN_URL = SITE_INDEX

    COMICID_PATTERN = re.compile(r'/home/book/index/id/(\d+)/?')
    DEFAULT_COMICID = '13287'
    DEFAULT_SEARCH_NAME = '的'
    DEFAULT_TAG = ""

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, '/home/book/index/id/%s/' % comicid)

    def get_comicbook_item(self):
        html_code, soup = self.get_html_and_soup(self.source_url)
        desc = soup.find('span', {'class': 'detail-text'}).text.strip()
        name = html.unescape(soup.h1.text.strip())
        author = ''
        last_update_time = ''
        tags = []
        for item in soup.find_all('p', {'class': 'data'}):
            if '作者：' in item.text:
                author = item.a.text.strip()
            if '最后更新：' in item.text:
                last_update_time = item.text.replace('最后更新：', '').strip()
            if '标签：' in item.text:
                for a in item.find_all('a'):
                    tag = a.text.strip()
                    tags.append(tag)
        style = soup.find('span', {'class': 'pic'}).get('style')
        cover_image_url = re.search(r'background\-image: url\((.*?)\);', style).group(1)
        cover_image_url = urljoin(self.SITE_INDEX, cover_image_url)
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       source_url=self.source_url,
                                       last_update_time=last_update_time)
        s = re.findall(r'let data = JSON.parse\((.*?)\)', html_code)[-1]
        data = json.loads(json.loads(s))
        for chapter_number, item in enumerate(data['list'], start=1):
            source_url = urljoin(self.SITE_INDEX, '/home/book/capterid/%s' % item['id'])
            title = item['title']
            image_urls = [urljoin(self.SITE_INDEX, i) for i in item['imagelist'].split(',')]
            book.add_chapter(chapter_number=chapter_number,
                             source_url=source_url,
                             image_urls=image_urls,
                             title=title)
        for tag in tags:
            book.add_tag(tag=tag, name=tag)
        return book

    def get_chapter_image_urls(self, citem):
        return citem.image_urls

    def latest(self, page=1):
        url = urljoin(self.SITE_INDEX, '/home/api/getpage/tp/1-newest-%s' % (page - 1))
        data = self.get_json(url)
        return self.parse_book_list(data)

    def get_tags(self):
        url = urljoin(self.SITE_INDEX, "/home/book/cate.html")
        soup = self.get_soup(url)
        tags = self.new_tags_item()
        for idx, ul in enumerate(soup.find('div', {'class': 'item'}).find_all('ul'), start=1):
            category = '分类%s' % idx
            for li in ul.find_all('li'):
                tag_name = li.a.text.strip()
                tag = li.a.get('data-value')
                tags.add_tag(category=category, name=tag_name, tag='c%s_%s' % (idx, tag))
        return tags

    def get_tag_result(self, tag, page=1):
        t1 = '2'
        t2 = '0'
        t3 = '0'
        for i in tag.split(','):
            if i.startswith('c1_'):
                t1 = i.replace('c1_', '')
            elif i.startswith('c2_'):
                t2 = i.replace('c2_', '')
            elif i.startswith('c3_'):
                t3 = i.replace('c3_', '')
            else:
                t3 = i
        url = urljoin(
            self.SITE_INDEX,
            "/home/api/cate/tp/1-{t3}-{t1}-1-{page}-{t2}-2-1".format(t1=t1, t2=t2, t3=t3, page=page)
        )
        data = self.get_json(url)
        return self.parse_book_list(data)

    def parse_book_list(self, data):
        result = self.new_search_result_item()
        for item in data['result']['list']:
            comicid = item['id']
            source_url = self.get_source_url(comicid)
            name = item['title']
            cover_image_url = urljoin(self.SITE_INDEX, item['image'])
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def search(self, name, page, size=None):
        url = urljoin(
            self.SITE_INDEX,
            "/home/api/searchk?keyword=%s&type=1&pageNo=%s" % (name, page)
        )
        data = self.get_json(url)
        return self.parse_book_list(data)

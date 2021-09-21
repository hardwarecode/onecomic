import re
import logging
from urllib.parse import urljoin

from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class KuimhCrawler(CrawlerBase):

    SITE = "kuimh"
    SITE_INDEX = 'https://www.kuimh.com/'
    SOURCE_NAME = "酷爱漫画"
    LOGIN_URL = SITE_INDEX

    COMICID_PATTERN = re.compile(r'/book/(mh\d+)/?')
    DEFAULT_COMICID = 'mh10968'
    DEFAULT_SEARCH_NAME = '少女'
    DEFAULT_TAG = ""

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, '/book/%s' % comicid)

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        desc = soup.find('p', {'class': 'content'}).text.strip()
        name = soup.h1.text.strip()
        author = ''
        last_update_time = ''
        tags = []
        for item in soup.find_all('p', {'class': 'subtitle'}):
            if '作者：' in item.text:
                author = item.text.replace('作者：', '').strip()
            if '最后更新：' in item.text:
                last_update_time = item.text.replace('最后更新：', '').strip()
            if '标签：' in item.text:
                for a in item.find_all('a'):
                    tag = a.text.strip()
                    tags.append(tag)
        cover_image_url = soup.find('div', {'class': 'cover'}).img.get('src')
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       source_url=self.source_url,
                                       last_update_time=last_update_time)
        li_list = soup.find('ul', {'id': 'detail-list-select'}).find_all('li')
        for chapter_number, li in enumerate(li_list, start=1):
            a = li.find_all('a')[-1]
            href = a.get('href')
            source_url = urljoin(self.SITE_INDEX, href)
            title = a.text.strip()
            book.add_chapter(chapter_number=chapter_number,
                             source_url=source_url,
                             title=title)

        for item in soup.find_all('span', {'class': 'block'}):
            if '标签：' in item.text:
                for a in item.find_all('a'):
                    tag = a.text
                    book.add_tag(tag=tag, name=tag)
        return book

    def get_chapter_image_urls(self, citem):
        soup = self.get_soup(citem.source_url)
        image_urls = []
        for i in soup.find('div', {'class': 'comicpage'}).find_all('img'):
            image_url = i.get('data-echo') or i.get('src')
            image_urls.append(image_url)
        return image_urls

    def latest(self, page=1):
        url = urljoin(self.SITE_INDEX, '/booklist?end=0&page=%s' % page)
        soup = self.get_soup(url)
        return self.parse_book_list(soup)

    def get_tags(self):
        url = urljoin(self.SITE_INDEX, "/booklist")
        soup = self.get_soup(url)
        tags = self.new_tags_item()
        for dl in soup.find_all('dl'):
            category = dl.dt.text.strip().replace(':', '').replace(' ', '')
            for dd in dl.find_all('dd'):
                tag_name = dd.a.text.strip()
                tag = dd.get('data-val')
                tags.add_tag(category=category, name=tag_name, tag='%s_%s' % (category, tag))
        return tags

    def get_tag_result(self, tag, page=1):
        ticai = '全部'
        diqu = '-1'
        jindu = '-1'
        for i in tag.split(','):
            if i.startswith('题材_'):
                ticai = i.replace('题材_', '')
            elif i.startswith('地区_'):
                diqu = i.replace('地区_', '')
            elif i.startswith('进度_'):
                jindu = i.replace('进度_', '')
            else:
                ticai = i
        params = {
            'tag': ticai,
            'end': jindu,
            'area': diqu,
            'page': page
        }
        url = urljoin(self.SITE_INDEX, "/booklist")
        soup = self.get_soup(url, params=params)
        return self.parse_book_list(soup)

    def parse_book_list(self, soup):
        result = self.new_search_result_item()
        for li in soup.find('ul', {'class': 'mh-list col7'}).find_all('li'):
            href = li.a.get('href')
            comicid = self.get_comicid_by_url(href)
            source_url = self.get_source_url(comicid)
            name = li.a.get('title')
            style = li.a.p.get('style')
            cover_image_url = re.search(r'background-image: url\((.*?)\)', style).group(1)
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def search(self, name, page, size=None):
        if page > 1:
            return self.new_search_result_item()
        url = urljoin(
            self.SITE_INDEX, "/search?keyword=%s" % name
        )
        soup = self.get_soup(url)
        return self.parse_book_list(soup)

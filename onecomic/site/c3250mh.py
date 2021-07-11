import re
import logging
from urllib.parse import urljoin

from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class C3250mhCrawler(CrawlerBase):

    SITE = "3250mh"
    SITE_INDEX = 'https://www.3250mh.com/'
    SOURCE_NAME = "3250漫画"
    LOGIN_URL = SITE_INDEX

    DEFAULT_COMICID = '1966'
    DEFAULT_SEARCH_NAME = '耽美'
    DEFAULT_TAG = "tag_搞笑"
    COMICID_PATTERN = re.compile(r'/manhua/(\d+)\.html')

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, "/manhua/{}.html".format(comicid))

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        name = soup.find('h1', {'class', 'title'}).text.strip()
        author = soup.find('div', {'class', 'title-warper'}).span.text.replace('作者：', '').strip()

        desc = soup.find('div', {'class': 'desc-con'}).text.strip()
        cover_image_url = soup.find('div', {'class', 'comic-cover'}).img.get('data-src')
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       source_url=self.source_url)

        li_list = soup.find('ul', {'id': 'chapterList'}).find_all('li')
        for chapter_number, li in enumerate(li_list, start=1):
            href = li.a.get('href')
            url = urljoin(self.SITE_INDEX, href)
            title = li.a.text.strip()
            book.add_chapter(chapter_number=chapter_number,
                             source_url=url,
                             title=title)
        try:
            a = soup.find('div', {'id': 'randomColor'}).a
            name = a.text.strip()
            href = a.get('href')
            tag = re.search(r'/booklist/\?tag=([^&]*)', href).group(1)
            book.add_tag(name=name, tag='tag_%s' % tag)
        except Exception:
            pass
        return book

    def get_chapter_image_urls(self, citem):
        soup = self.get_soup(citem.source_url)
        image_urls = [div.img.get('src') for div in
                      soup.find('div', {'class': 'comiclist'}).find_all('div', {'class': 'comicpage'})]
        return image_urls

    def latest(self, page=1):
        url = urljoin(self.SITE_INDEX, "/update.html?page=%s" % page)
        soup = self.get_soup(url)
        result = self.new_search_result_item()
        for li in soup.find('ul', {'class': 'comic-update'}).find_all('li'):
            href = li.a.get('href')
            comicid = self.get_comicid_by_url(href)
            source_url = urljoin(self.SITE_INDEX, href)
            name = li.a.get('title').strip()
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url='',
                              source_url=source_url)
        return result

    def get_tags(self):
        url = 'https://www.3250mh.com/booklist.html'
        soup = self.get_soup(url)
        tags = self.new_tags_item()
        for a in soup.find('dl', {'class': 'filter'}).find('dd', {'id': 'tags'}).find_all('a'):
            tag = a.get('data-val').strip()
            name = a.text.strip()
            tags.add_tag(category='题材', name=name, tag='tag_%s' % tag)

        for a in soup.find('dl', {'class': 'filter'}).find('dd', {'id': 'areas'}).find_all('a'):
            tag = a.get('data-val').strip()
            name = a.text.strip()

            tags.add_tag(category='地区', name=name, tag='area_%s' % tag)
        for a in soup.find('dl', {'class': 'filter'}).find('dd', {'id': 'end'}).find_all('a'):
            tag = a.get('data-val').strip()
            name = a.text.strip()
            tags.add_tag(category='进度', name=name, tag='end_%s' % tag)
        return tags

    def parse_book_list(self, soup):
        result = self.new_search_result_item()
        for li in soup.find('div', {'id': 'comicListBox'}).ul.find_all('li'):
            href = li.a.get('href')
            comicid = self.get_comicid_by_url(href)
            source_url = urljoin(self.SITE_INDEX, href)
            name = li.a.get('title').strip()
            cover_image_url = li.a.img.get('src')
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def get_tag_result(self, tag, page=1):
        params = {'page': page}
        for t in tag.split(','):
            if t.startswith('tag_'):
                params['tag'] = t.replace('tag_', '')
            elif t.startswith('area_'):
                params['area'] = t.replace('area_', '')
            elif t.startswith('end_'):
                params['end'] = t.replace('end_', '')
        url = "https://www.3250mh.com/booklist"
        soup = self.get_soup(url, params=params)
        return self.parse_book_list(soup)

    def search(self, name, page=1, size=None):
        params = {'page': page, 'keyword': name}
        url = "https://www.3250mh.com/search"
        soup = self.get_soup(url, params=params)
        return self.parse_book_list(soup)

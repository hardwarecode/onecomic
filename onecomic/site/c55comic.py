import re
import logging
from urllib.parse import urljoin

from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class C55comicCrawler(CrawlerBase):

    SITE = "55comic"
    SITE_INDEX = 'https://www.55comic.com/'
    SOURCE_NAME = "污污漫画"
    LOGIN_URL = SITE_INDEX
    R18 = True

    COMICID_PATTERN = re.compile(r'/book/(\d+)/?')
    DEFAULT_COMICID = '871'
    DEFAULT_SEARCH_NAME = '姐姐'
    DEFAULT_TAG = ""

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, '/book/%s' % comicid)

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        name = soup.h1.text.strip()
        author = soup.find('p', {'class': 'author'}).span.text.strip()
        desc = soup.find('p', {'class': 'detail-docu'}).text.strip()
        cover_image_url = soup.find('div', {'class': 'detail-cover'}).img.get('src')
        status = soup.find('span', {'class': 'label'}, text='狀態：')\
            .previous.text.replace('狀態：', '').strip()
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       status=status,
                                       source_url=self.source_url)
        for chapter_number, li in enumerate(
                soup.find('div', {'id': 'cata_cont_list'}).find_all('li'), start=1):
            href = li.a.get('href')
            source_url = urljoin(self.SITE_INDEX, href)
            title = li.a.get('title')
            book.add_chapter(chapter_number=chapter_number,
                             source_url=source_url,
                             title=title)
        for a in soup.find('span', {'class': 'label'}, text='標簽：').previous.find_all('a'):
            tag_name = a.text.strip()
            book.add_tag(tag=tag_name, name=tag_name)
        return book

    def get_chapter_image_urls(self, citem):
        soup = self.get_soup(citem.source_url)
        image_urls = [img.get('data-original')
                      for img in soup.find('div', {'class': 'comicpage'}).find_all('img')]
        return image_urls

    def latest(self, page=1):
        soup = self.get_soup(self.SITE_INDEX)
        result = self.new_search_result_item()
        for li in soup.find('div', {'class': 'mod-con daily_update J_block'}).find_all('li'):
            href = li.a.get('href')
            comicid = self.get_comicid_by_url(href)
            source_url = urljoin(self.SITE_INDEX, href)
            name = li.p.text.strip()
            cover_image_url = li.a.img.get('src')
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def get_tags(self):
        url = urljoin(self.SITE_INDEX, "/booklist")
        soup = self.get_soup(url)
        tags = self.new_tags_item()
        for div in soup.find_all('div', {'class': 'classify-container'}):
            category = div.find('div', {'class': 'classify-tit'}).text.strip()
            for li in div.find_all('li'):
                tag_name = li.a.text.strip()
                tags.add_tag(category=category, name=tag_name, tag=tag_name)
        return tags

    def get_tag_result(self, tag, page=1):
        area = '-1'
        tag_id = ''
        end = '-1'
        for tag_name in tag.split(','):
            if '已完結' == tag_name:
                end = '1'
            elif '連載中' == tag_name:
                end == '0'
            elif '日漫' == tag_name:
                area = '1'
            else:
                tag_id = tag_name
        url = 'https://www.55comic.com/booklist?tag=%s&area=%s&end=%s&page=%s' % (tag_id, area, end, page)
        soup = self.get_soup(url)
        result = self.new_search_result_item()
        for li in soup.find('ul', {'class': 'cartoon-hot-ul cartoon-classify-ul'}).find_all('li'):
            href = li.a.get('href')
            comicid = self.get_comicid_by_url(href)
            source_url = urljoin(self.SITE_INDEX, href)
            name = li.p.text.strip()
            cover_image_url = li.a.img.get('src')
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def search(self, name, page, size=None):
        url = "https://www.55comic.com/search?keyword=%s" % name
        soup = self.get_soup(url)
        result = self.new_search_result_item()
        for li in soup.find('ul', {'class': 'mh-list col7'}).find_all('li'):
            href = li.a.get('href')
            comicid = self.get_comicid_by_url(href)
            source_url = urljoin(self.SITE_INDEX, href)
            name = li.p.text.strip()
            cover_image_url = li.a.img.get('src')
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

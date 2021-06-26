import re
import logging
from urllib.parse import urljoin

from ..crawlerbase import CrawlerBase
from ..worker import concurrent_run

logger = logging.getLogger(__name__)


class TwhentaiCrawler(CrawlerBase):

    SITE = "twhentai"
    SITE_INDEX = 'http://twhentai.com/'
    SOURCE_NAME = "TwHentai"
    LOGIN_URL = SITE_INDEX
    R18 = True
    SINGLE_CHAPTER = True

    COMICID_PATTERN = re.compile(r'twhentai\.com/([_a-zA-Z0-9]+/\d+)/?')
    DEFAULT_COMICID = 'hentai_doujin-86561'
    DEFAULT_SEARCH_NAME = '姐姐'
    DEFAULT_TAG = ""
    SITE_ENABLE = False

    @classmethod
    def get_comicid_by_url(cls, comicid_or_url):
        if comicid_or_url and isinstance(comicid_or_url, str):
            r = cls.COMICID_PATTERN.search(comicid_or_url)
            comicid = r.group(1) if r else comicid_or_url
            return comicid.replace("/", "-")
        return comicid_or_url

    @property
    def source_url(self):
        return self.get_source_url(self.comicid.replace("-", "/"))

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, '/%s/' % comicid)

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        name = soup.h3.text.strip()
        author = ''
        desc = ''
        p1_image_urls = self.parse_page_images(soup)
        for div in soup.find_all('div', {'class': 'recommended-grids'}):
            for img in div.find_all('img'):
                p1_image_urls.append
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=p1_image_urls[0],
                                       author=author,
                                       source_url=self.source_url)
        li = soup.find('ul', {'class': 'pagination pagination'}).find_all('li')[-1]
        r = re.search(r'\d+_p(\d+)/?', li.a.get('href'))
        total_page = int(r.group(1)) if r else 1
        book.add_chapter(chapter_number=1,
                         source_url=self.source_url,
                         title='',
                         total_page=total_page,
                         p1_image_urls=p1_image_urls)
        for li in soup.find('div', {'class': 'show-right-grids'}).ul.find_all('li'):
            tag_name = li.a.span.text.replace('H漫', '').strip()
            book.add_tag(tag=tag_name, name=tag_name)
        return book

    def parse_page_images(self, soup):
        image_urls = []
        for div in soup.find_all('div', {'class': 'recommended-grids'}):
            for img in div.find_all('img'):
                url = img.get('src')
                url = re.sub(r'-thumb\d+x\d+', '', url)
                if not url.startswith('http'):
                    url = urljoin(self.SITE_INDEX, url)
                image_urls.append(url)
        return image_urls

    def get_chapter_image_urls(self, citem):
        image_urls = citem.p1_image_urls

        def _func(page):
            url = citem.source_url.rstrip('/') + '_p%s/' % page
            soup = self.get_soup(url)
            urls = self.parse_page_images(soup)
            return urls

        zip_args = []
        for page in range(2, citem.total_page + 1):
            zip_args.append((_func, dict(page=page)))
        result = concurrent_run(zip_args=zip_args)
        logger.info('result=', result)
        for urls in result:
            if urls:
                image_urls.extend(urls)
        return image_urls

    def parse_book_list(self, soup):
        result = self.new_search_result_item()
        for div in soup.find('div', {'class': 'recommended'})\
                .find_all('div', {'class': 'recommended-grids'}, recursive=False):
            for d in div.find_all('div', 'col-md-3 resent-grid recommended-grid'):
                href = d.a.get('href')
                source_url = urljoin(self.SITE_INDEX, href)
                comicid = self.get_comicid_by_url(source_url)
                name = d.h5.text.strip()
                cover_image_url = d.img.get('src')
                if not cover_image_url.startswith('http'):
                    cover_image_url = urljoin(self.SITE_INDEX, cover_image_url)
                result.add_result(comicid=comicid,
                                  name=name,
                                  cover_image_url=cover_image_url,
                                  source_url=source_url)
        return result

    def latest(self, page=1):
        url = "http://twhentai.com/hentai_manga/"
        if page > 1:
            url = 'http://twhentai.com/hentai_manga/page_%s.html' % page
        soup = self.get_soup(url)
        return self.parse_book_list(soup)

    def get_tags(self):
        url = urljoin(self.SITE_INDEX, "/taglist")
        soup = self.get_soup(url)
        tags = self.new_tags_item()
        for h5 in soup.find('div', {'class': 'recommended'}).find_all('h5'):
            tag_name = h5.a.text.strip()
            tag_name = re.sub(r'\(\d+\)', '', tag_name)
            tags.add_tag(category='热门标签', name=tag_name, tag=tag_name)
        return tags

    def get_tag_result(self, tag, page=1):
        if not tag:
            return self.latest(page=page)
        if page > 1:
            url = 'http://twhentai.com/tag/%s/%s/' % (tag, page)
        else:
            url = "http://twhentai.com/tag/%s/" % tag
        soup = self.get_soup(url)
        return self.parse_book_list(soup)

    def search(self, name, page, size=None):
        if page > 1:
            url = 'http://twhentai.com/search/%s/%s/' % (name, page)
        else:
            url = 'http://twhentai.com/search/%s/' % name
        soup = self.get_soup(url)
        return self.parse_book_list(soup)

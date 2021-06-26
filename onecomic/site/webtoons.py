import re
import logging
from urllib.parse import urljoin

from ..crawlerbase import CrawlerBase
from ..worker import concurrent_run

logger = logging.getLogger(__name__)


class WebtoonsCrawler(CrawlerBase):

    SITE = "webtoons"
    SITE_INDEX = 'https://www.webtoons.com/'
    SOURCE_NAME = "WEBTOONS"
    LOGIN_URL = SITE_INDEX
    COMICID_PATTERN = re.compile(r'title_no=(\d+)')
    DEFAULT_COMICID = '2048'
    DEFAULT_SEARCH_NAME = ''
    DEFAULT_TAG = ""
    SITE_ENCODEING = 'utf-8'

    @property
    def source_url(self):
        if not hasattr(self, '_source_url'):
            self._source_url = self.get_source_url(self.comicid)
        return self._source_url

    def get_source_url(self, comicid):
        url = urljoin(self.SITE_INDEX, "/_/_/_/list?title_no={}".format(comicid))
        response = self.send_request('get', url)
        return str(response.url)

    def get_chapters_from_page(self, soup):
        chapters = []
        for li in soup.find('ul', {'id': '_listUl'}).find_all('li'):
            href = li.a.get('href')
            title = li.find('span', {'class': 'subj'}).text
            url = urljoin(self.SITE_INDEX, href)
            chapters.append(dict(source_url=url, title=title))
        total_page = 1
        total_page = int(soup.find('div', {'class': 'paginate'}).find_all('a')[-1].span.text)
        return total_page, chapters

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        name = soup.find('h1', {'class': 'subj'}).text
        author_tag = soup.find('h1', {'class': 'subj'}).parent
        author_tag.a.span.decompose()
        author = author_tag.a.text.strip()
        desc = soup.find('p', {'class': 'summary'}).text
        style = soup.find('div', {'class': 'detail_body banner'}).get('style')
        cover_image_url = re.search(r'url\((.*?)\)', style).group(1)
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       source_url=self.source_url)
        chapters = []
        total_page, page_chapters = self.get_chapters_from_page(soup)
        chapters.extend(page_chapters)

        def get_page_chapters(page):
            s = self.get_soup(self.source_url, params={'page': page})
            _, c = self.get_chapters_from_page(s)
            return c

        zip_args = []
        for page in range(2, total_page + 1):
            zip_args.append((get_page_chapters, dict(page=page)))
        result_list = concurrent_run(zip_args)
        for result in result_list:
            chapters.extend(result)

        for chapter_number, c in enumerate(reversed(chapters), start=1):
            book.add_chapter(
                chapter_number=chapter_number,
                source_url=c['source_url'],
                title=c['title'])
        return book

    def get_chapter_image_urls(self, citem):
        headers = {'Referer': citem.source_url}
        soup = self.get_soup(citem.source_url, headers=headers)
        image_urls = [img.get('data-url') for img in soup.find('div', {'id': '_imageList'}).find_all('img')]
        return image_urls

    def latest(self, page=1):
        if page >= 2:
            return self.new_search_result_item()
        result = self.new_search_result_item()
        url = "https://www.webtoons.com/zh-hant/dailySchedule"
        soup = self.get_soup(url)
        for ul in soup.find_all('ul', {'class': 'daily_card'}):
            for li in ul.find_all('li'):
                href = li.a.get('href')
                source_url = urljoin(self.SITE_INDEX, href)
                comicid = self.get_comicid_by_url(source_url)
                name = li.find('p', {'class': 'subj'}).text
                cover_image_url = li.img.get('src')
                result.add_result(comicid=comicid,
                                  name=name,
                                  cover_image_url=cover_image_url,
                                  source_url=source_url)
        return result

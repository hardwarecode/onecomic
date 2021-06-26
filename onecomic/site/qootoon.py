import re
import logging
from urllib.parse import urljoin

from ..crawlerbase import CrawlerBase
from ..exceptions import ChapterNotFound

logger = logging.getLogger(__name__)


class QootoonCrawler(CrawlerBase):

    SITE = "qootoon"
    SITE_INDEX = 'https://www.qootoon.net/'
    SOURCE_NAME = "qootoon"
    LOGIN_URL = SITE_INDEX
    COMICID_PATTERN = re.compile(r'/\#contents_\d+')
    DEFAULT_COMICID = '107'
    DEFAULT_SEARCH_NAME = ''
    DEFAULT_TAG = ""
    SITE_ENCODEING = 'utf-8'

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, "/#contents_80668".format(comicid))

    def get_comicbook_item(self):
        url = urljoin(self.SITE_INDEX, "/comic/contents_list?comic_id=%s" % self.comicid)
        soup = self.get_soup(url)
        name = soup.find('div', {'id': 'tab1_board'}).div.div.text
        style = soup.find('div', {'id': 'tab1_board'}).get('style')
        cover_image_url = re.search(r"""url\('(.*?)'\)""", style).group(1)
        author = ''
        for font in soup.find('div', {'id': 'tab1_board'}).find_all('font'):
            text = font.text.strip()
            if '作家 :' in text:
                author = text.replace('作家 :', '').strip().replace('&amp;', '&')
        desc = ''
        try:
            desc_div = soup.find('div', {'id': 'tab1_board'}).div.find_all('div', recursive=False)[1]
            desc_div.dev.decompose()
            desc = desc_div.text.strip()
        except Exception:
            pass

        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       source_url=self.source_url)
        idx = 1
        for div in soup.find('div', {'class': 'filtr-container'}).find_all('div', recursive=False)[1:]:
            onclick = div.get('onclick', '')
            r = re.search(r'''episode_click\('(\d+)'\);''', onclick)
            if not r:
                continue
            episode = r.group(1)
            table = div.table
            title = table.span.text.strip()
            url = urljoin(self.SITE_INDEX, '/#contents_%s,%s' % (self.comicid, episode))
            book.add_chapter(chapter_number=idx,
                             source_url=url,
                             episode=episode,
                             title=title)
            idx += 1
        return book

    def get_chapter_image_urls(self, citem):
        url = urljoin(
            self.SITE_INDEX,
            'https://www.qootoon.net/comic/episode_view?episode_idx=%s' % citem.episode
        )
        headers = {
            'referer': 'https://www.qootoon.net/',
            'sec-fetch-site': 'same-origin',
        }
        soup = self.get_soup(url, headers=headers)

        image_urls = []
        container = soup.find('div', {'class': 'swiper-container'})
        if not container:
            raise ChapterNotFound.from_template(site=self.SITE,
                                                comicid=self.comicid,
                                                chapter_number=citem.chapter_number,
                                                source_url=citem.source_url)
        for div in container.find_all('div', recursive=False):
            if div.img:
                image_url = div.img.get('src')
                image_urls.append(image_url)
        return image_urls

    def latest(self, page):
        if page >= 2:
            return self.new_search_result_item()
        url = 'https://www.qootoon.net/page/complete?data=new'
        soup = self.get_soup(url)
        result = self.new_search_result_item()
        for div in soup.find('div', {'id': 'list_data_cut'}).find_all('div', recursive=False):
            comicid = re.search(r'contents_cell_(\d+)', div.get('id')).group(1)
            source_url = self.get_source_url(comicid)
            name = div.find('span', {'class': 'cc9'}).text.strip()
            cover_image_url = div.find('div', {'class': 'cc7'}).div.get('data-src')
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

import re
import json
from urllib.parse import urljoin
import logging

import execjs
import lzstring

from ..crawlerbase import CrawlerBase
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ManhuaguiCrawler(CrawlerBase):

    SITE = "manhuagui"
    SITE_INDEX = "https://www.manhuagui.com/"
    DOMAIN = ".manhuagui.com"
    SOURCE_NAME = "漫画柜"

    IMAGE_URL_PREFIX = 'https://i.hamreus.com'
    LOGIN_URL = urljoin(SITE_INDEX, "/user/login")
    COMICID_PATTERN = re.compile(r'/comic/(\d+)/?')
    REQUIRE_JAVASCRIPT = True

    DEFAULT_COMICID = '19430'
    DEFAULT_SEARCH_NAME = '鬼灭之刃'
    TAGS = [
        dict(name='连载漫画', tag='lianzai'),
        dict(name='完结漫画', tag='wanjie'),
    ]

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, "/comic/{}/".format(comicid))

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        name = soup.find('div', {'class': 'book-title'}).h1.text
        desc = soup.find('div', {'id': 'intro-all'}).p.text

        li_list = soup.find('ul', {'class': 'detail-list'}).find_all('li')
        tag_soup = li_list[1].find_all('strong')[0]
        author_soup = li_list[1].find_all('strong')[1]
        author = author_soup.previous_element.a.get('title')
        img = soup.find('div', attrs={'class': 'book-cover'}).p.img
        cover_image_url = img.get('data-src') or img.get('src')
        status = soup.find('li', {'class': 'status'}).span.span.text
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       source_url=self.source_url,
                                       status=status)
        for a in tag_soup.previous_element.find_all('a'):
            name = a.get('title')
            href = a.get('href')
            tag = href.replace('/list/', '').replace('/', '')
            book.add_tag(name=name, tag=tag)

        chapter_soup = soup.find('div', {'class': 'chapter'})
        adult_input = soup.find('input', {'id': '__VIEWSTATE'})
        if adult_input is not None:
            adult_encoded_value = adult_input.get('value')
            if len(adult_encoded_value) > 0:
                adult_decoded_value = lzstring.LZString().decompressFromBase64(adult_encoded_value)
                chapter_soup = BeautifulSoup(adult_decoded_value, 'html.parser')
        h4_list = chapter_soup.find_all('h4')
        div_list = chapter_soup.find_all('div', {'class': 'chapter-list'})
        idx = 1
        ext_idx = {}
        for h4, div in zip(h4_list, div_list):
            for ul in div.find_all('ul'):
                for li in reversed(ul.find_all('li')):
                    href = li.a.get('href')
                    title = li.a.get('title')
                    full_url = urljoin(self.SITE_INDEX, href)
                    if h4.text.strip() == '单话' or len(h4_list) == 1:
                        book.add_chapter(chapter_number=idx, title=title, source_url=full_url)
                        idx += 1
                    else:
                        name = h4.text.strip()
                        ext_idx.setdefault(name, 1)
                        book.add_chapter(chapter_number=ext_idx[name], title=title, ext_name=name, source_url=full_url)
                        ext_idx[name] += 1
        return book

    def get_image_data_from_page(self, html):
        js = re.search(r">window.*(\(function\(p.*?)</script>", html).group(1)
        b64_str = re.search(r"[0-9],'([A-Za-z0-9+/=]+?)'", js).group(1)
        s = lzstring.LZString.decompressFromBase64(b64_str)
        new_js = re.sub(r"'[A-Za-z0-9+/=]*'\[.*\]\('\\x7c'\)", "'" + s + "'.split('|')", js)
        res = execjs.eval(new_js)
        return json.loads(re.search(r"(\{.*\})", res).group(1))

    def get_chapter_image_urls(self, citem):
        html = self.get_html(citem.source_url)
        data = self.get_image_data_from_page(html)
        image_urls = []
        for i in data['files']:
            url = self.IMAGE_URL_PREFIX + data['path'] + i + '?e=%(e)s&m=%(m)s' % (data['sl'])
            image_urls.append(url)
        return image_urls

    def search(self, name, page=1, size=None):
        url = urljoin(self.SITE_INDEX, '/s/{}_p{}.html'.format(name, page))
        soup = self.get_soup(url)
        li_list = soup.find_all('li', {'class': 'cf'})
        result = self.new_search_result_item()
        for li_soup in li_list:
            name = li_soup.find('div', {'class': 'book-cover'}).a.get('title')
            img = li_soup.find('div', {'class': 'book-cover'}).a.img
            cover_image_url = img.get('data-src') or img.get('src')
            href = li_soup.find('div', {'class': 'book-cover'}).a.get('href')
            comicid = href.split('/')[2]
            source_url = self.get_source_url(comicid)
            status = li_soup.find('span', {'class': 'tt'}).text
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url,
                              status=status)
        return result

    def latest(self, page=1):
        url = urljoin(self.SITE_INDEX, '/update/')
        soup = self.get_soup(url)
        result = self.new_search_result_item()
        for div in soup.find_all('div', {'class': 'latest-list'})[page - 1:page]:
            for li in div.find_all('li'):
                name = li.img.get('alt')
                cover_image_url = li.img.get('data-src') or li.img.get('src')
                href = li.a.get('href')
                comicid = href.split('/')[2]
                source_url = self.get_source_url(comicid)
                status = li.find('span', {'class': 'tt'}).text
                result.add_result(comicid=comicid,
                                  name=name,
                                  cover_image_url=cover_image_url,
                                  source_url=source_url,
                                  status=status)
        return result

    def get_tags(self):
        item = self.new_tags_item()
        url = urljoin(self.SITE_INDEX, '/list/')
        soup = self.get_soup(url)
        div_list = soup.find('div', {'class': 'filter-nav'}).find_all('div', {'class': 'filter'})
        for idx, div in enumerate(div_list, start=1):
            category = div.label.get_text().strip().replace('：', '')
            for li in div.find_all('li'):
                name = li.a.text
                tag = li.a.get('href').replace('/list/', '').replace('/', '')
                if tag:
                    tag = '%s_%s' % (idx, tag)
                    item.add_tag(category=category, name=name, tag=tag)
        return item

    def get_tag_result(self, tag, page=1):
        result = self.new_search_result_item()
        if tag:
            params = {}
            for i in tag.split(','):
                if re.match(r'\d+_.*', i):
                    idx, t = i.split('_', 1)
                    params[int(idx)] = t
                else:
                    params[0] = i
            query = '_'.join([i[1] for i in sorted(params.items(), key=lambda x: x[0])])
            url = urljoin(self.SITE_INDEX, '/list/%s/index_p%s.html' % (query, page))
        else:
            url = urljoin(self.SITE_INDEX, '/list/index_p%s.html' % (query, page))

        soup = self.get_soup(url)
        ul = soup.find('ul', {'id': 'contList'})
        if not ul:
            return result
        for li in ul.find_all('li'):
            status = li.find('span', {'class': 'tt'}).text
            name = li.img.get('alt')
            cover_image_url = li.img.get('data-src') or li.img.get('src')
            href = li.a.get('href')
            comicid = href.split('/')[2]
            source_url = self.get_source_url(comicid)
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url,
                              status=status)
        return result

    def login(self):
        self.selenium_login(login_url=self.LOGIN_URL,
                            check_login_status_func=self.check_login_status)

    def check_login_status(self):
        session = self.get_session()
        if session.cookies.get("my", domain=".manhuagui.com"):
            return True


class MhguiCrawler(ManhuaguiCrawler, CrawlerBase):
    SITE = "mhgui"
    SITE_INDEX = "https://www.mhgui.com/"
    DOMAIN = ".mhgui.com"
    SOURCE_NAME = "漫画柜"
    IMAGE_URL_PREFIX = 'https://i.hamreus.com'

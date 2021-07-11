import json
import re
import logging
from urllib.parse import urljoin

from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class BoodoCrawler(CrawlerBase):

    SITE = "boodo"
    SITE_INDEX = 'https://boodo.qq.com/'
    SOURCE_NAME = "波动boodo"
    LOGIN_URL = SITE_INDEX

    DEFAULT_COMICID = '543172'
    DEFAULT_SEARCH_NAME = '和'
    DEFAULT_TAG = "0"
    COMICID_PATTERN = re.compile(r'/pages/comicDetail\.html\?id=(\d+)')

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, "/pages/comicDetail.html?id={}".format(comicid))

    def get_comicbook_item(self):
        html = self.get_html(self.source_url)
        js_str = re.search(r'<script>window\.__INITIAL_STATE__=(.*?)</script>', html).group(1)
        data = json.loads(js_str)
        baseinfo = data['page.comic.detail']['baseInfo']

        name = baseinfo['name']
        author = baseinfo['author']
        desc = baseinfo['desc']
        cover_image_url = baseinfo['coverImg'].replace('\\u002F', '/')
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       source_url=self.source_url)
        for item in baseinfo['category']:
            book.add_tag(name=item['name'], tag=item['id'])

        items = {}
        for item in data['page.comic.detail']['sectionList']:
            sectionID = item['sectionID']
            items[sectionID] = item
        left_sections = []
        for i in data['page.comic.detail']['sectionIdList']:
            if i not in items:
                left_sections.append(i)
        for i in range(0, len(left_sections), 100):
            chunk_ids = left_sections[i:i + 100]
            params = {
                '0': {
                    'module': 'comic_basic_operate_mt_svr',
                    'method': 'getSectionListWithPayStatus',
                    'param': {
                        'comicID': str(self.comicid),
                        'sectionIDList': chunk_ids
                    }
                }
            }
            api = "https://cgi.boodo.qq.com/cgi-bin/comicpc_async_cgi?_wv=1&_secondWebView=1&fromWeb=1&platId=110&mqqVersion=&app_version=0.0.0.0&app_platId=109&app_from=8&merge=1&p_tk=&fromWeb=1"
            response = self.send_request('POST', api, data={'param': json.dumps(params)})
            for sectionID, item in response.json()['data']['0']['retBody']['data']['sectionIndex'].items():
                items[sectionID] = item

            for chapter_number, item in enumerate(sorted(items.values(), key=lambda x: int(x['sectionID'])), start=1):
                sectionID = item['sectionID']
                url = "https://boodo.qq.com/pages/comic-reader.html?id=%s&sectionId=%s" % (self.comicid, sectionID)
                title = item['sectionName']
                book.add_chapter(chapter_number=chapter_number,
                                 source_url=url,
                                 title=title,
                                 sectionID=sectionID)
        return book

    def get_chapter_image_urls(self, citem):
        api = 'https://cgi.boodo.qq.com/cgi-bin/comicpc_async_cgi?_wv=1&_secondWebView=1&fromWeb=1&platId=110&mqqVersion=&app_version=0.0.0.0&app_platId=109&app_from=8&merge=5&p_tk=&fromWeb=1'
        params = {
            "0": {
                "module": "comic_basic_operate_mt_svr",
                "method": "QuerySectionDetail",
                "param": {
                    "comicId": str(self.comicid),
                    "sectionId": citem.sectionID
                }
            }
        }
        response = self.send_request('POST', api, data={'param': json.dumps(params)})
        image_urls = []
        for item in response.json()['data']['0']['retBody']['data']['picInfo']:
            image_urls.append(item['picUrl'])
        return image_urls

    def latest(self, page=1):
        url = urljoin(self.SITE_INDEX, "/pages/category.html?categoryType=1&category=0&page=%s" % page)
        soup = self.get_soup(url)
        return self.parse_book_list(soup)

    def get_tags(self):
        url = 'https://boodo.qq.com/pages/category.html?categoryType=1&category=0'
        soup = self.get_soup(url)
        tags = self.new_tags_item()
        for a in soup.find('div', {'class': 'mod-categorybar'}).ul.li.find_all('a'):
            name = a.text.strip()
            href = a.get('href')
            tag = re.search(r'category=(\d+)', href).group(1)
            tags.add_tag(category='题材', name=name, tag=tag)

        return tags

    def parse_book_list(self, soup):
        result = self.new_search_result_item()
        for li in soup.find('ul', {'class': 'list-comic-book ui-clfx'}).find_all('li'):
            href = li.a.get('href')
            comicid = self.get_comicid_by_url(href)
            source_url = urljoin(self.SITE_INDEX, href)
            cover_image_url = li.a.img.get('src')
            name = li.a.img.get('alt')
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def get_tag_result(self, tag, page=1):
        url = "https://boodo.qq.com/pages/category.html?categoryType=1&category=%s&page=%s" % (tag, page)
        soup = self.get_soup(url)
        return self.parse_book_list(soup)

    def search(self, name, page=1, size=None):
        if page > 1:
            return self.new_search_result_item()

        url = "https://boodo.qq.com/pages/search.html?keyword=%s" % name
        html = self.get_html(url)
        js_str = re.search(r'<script>window\.__INITIAL_STATE__=(.*?)</script>', html).group(1)
        data = json.loads(js_str)
        result = self.new_search_result_item()
        for item in data['page.search']['workLists']:
            try:
                comicid = int(item['id'])
            except Exception:
                continue
            source_url = self.get_source_url(comicid)
            name = item['name']
            cover_image_url = item['coverImg']
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

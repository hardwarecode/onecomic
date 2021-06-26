import re
import logging
from urllib.parse import urljoin
import random


from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class QimiaomhCrawler(CrawlerBase):

    SITE = "qimiaomh"
    SITE_INDEX = 'https://www.qimiaomh.com/'
    SOURCE_NAME = "奇妙漫画"
    LOGIN_URL = SITE_INDEX

    DEFAULT_COMICID = '7415'
    DEFAULT_SEARCH_NAME = '和'
    DEFAULT_TAG = "1"
    COMICID_PATTERN = re.compile(r'/manhua/(\d+)\.html')

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, "/manhua/{}.html".format(comicid))

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        name = soup.find('div', {'class', 'ctdbLeft'}).a.get('title').strip()
        soup.find('p', {'class': 'author'}).find('span', {'class': 'lineTit'}).decompose()
        author = soup.find('p', {'class': 'author'}).text.strip()

        desc = soup.find('p', {'id': 'worksDesc'}).text.strip()
        cover_image_url = soup.find('div', {'class', 'ctdbLeft'}).img.get('src')
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       source_url=self.source_url)

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

        ul_list = soup.find('div', {'class': 'comic-content-list'}).find_all('ul')
        for chapter_number, ul in enumerate(reversed(ul_list), start=current):
            href = ul.find('li', {'class': 'cimg'}).a.get('href')
            sid = re.search(r'/manhua/\d+/(\d+)\.html', href).group(1)
            url = urljoin(self.SITE_INDEX, href)
            title = ul.find('li', {'class': 'cimg'}).a.get('title')
            book.add_chapter(chapter_number=chapter_number,
                             source_url=url,
                             title=title,
                             sid=sid)

        return book

    def get_chapter_image_urls(self, citem):
        api_url = 'https://www.qimiaomh.com/Action/Play/AjaxLoadImgUrl?did=%s&sid=%s&tmp=%s' % (
            self.comicid, citem.sid, random.random())
        api_data = self.get_json(api_url)
        image_urls = api_data['listImg']
        return image_urls

    def latest(self, page=1):
        url = urljoin(self.SITE_INDEX, "/list-1------updatetime--%s.html" % page)
        soup = self.get_soup(url)
        return self.parse_book_list(soup)

    def parse_book_list(self, soup):
        result = self.new_search_result_item()
        for div in soup.find('div', {'class': 'mt20'}).find_all('div', {'class': 'classification'}):
            href = div.a.get('href')
            comicid = self.get_comicid_by_url(href)
            source_url = urljoin(self.SITE_INDEX, href)
            name = div.a.text.strip()
            cover_image_url = div.img.get('data-src') or div.img.get('src')
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def get_tags(self):
        tags = self.new_tags_item()
        for name, tag in [
            ('热血', 7),
            ('恋爱', 8),
            ('青春', 9),
            ('彩虹', 10),
            ('冒险', 11),
            ('后宫', 12),
            ('悬疑', 13),
            ('玄幻', 14),
            ('穿越', 16),
            ('都市', 17),
            ('腹黑', 18),
            ('爆笑', 19),
            ('少年', 20),
            ('奇幻', 21),
            ('古风', 22),
            ('妖恋', 23),
            ('元气', 24),
            ('治愈', 25),
            ('励志', 26),
            ('日常', 27),
            ('百合', 28),
        ]:
            tags.add_tag(category='题材', name=name, tag='ticai_%s' % tag)
        for name, tag in [
            ('国漫', '国漫'),
            ('日漫', '日漫'),
            ('韩漫', '韩漫'),
        ]:
            tags.add_tag(category='地区', name=name, tag='diqu_%s' % tag)

        for name, tag in [
            ('连载', 1),
            ('完结', 0)
        ]:
            tags.add_tag(category='状态', name=name, tag='zhuangtai_%s' % tag)
        return tags

    def get_tag_result(self, tag, page=1):
        ticai = ''
        diqu = ''
        zhuangtai = ''
        for t in tag.split(','):
            if t.startswith('ticai_'):
                ticai = t.replace('ticai_', '')
            elif t.startswith('diqu_'):
                diqu = t.replace('diqu_', '')
            elif t.startswith('zhuangtai_'):
                zhuangtai = t.replace('zhuangtai_', '')
        url = 'https://www.qimiaomh.com/list-1-{ticai}-{diqu}----updatetime-{zhuangtai}-{page}.html'\
            .format(ticai=ticai, diqu=diqu, zhuangtai=zhuangtai, page=page)
        soup = self.get_soup(url)
        return self.parse_book_list(soup)

    def search(self, name, page=1, size=None):
        url = "https://www.qimiaomh.com/action/Search?keyword=%s&page=%s" % (name, page)
        soup = self.get_soup(url)
        return self.parse_book_list(soup)

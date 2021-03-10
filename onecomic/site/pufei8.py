import re
import logging
import base64
from urllib.parse import urljoin

import jsbeautifier

from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class Pufei8Crawler(CrawlerBase):

    SITE = "pufei8"
    SITE_INDEX = 'http://www.pufei8.com/'
    SOURCE_NAME = "扑飞漫画"
    LOGIN_URL = SITE_INDEX
    COMICID_PATTERN = re.compile(r'/manhua/(\d+)/index.html')
    DEFAULT_COMICID = '419'
    DEFAULT_SEARCH_NAME = '一人之下'
    DEFAULT_TAG = "shaonianrexue"
    SITE_ENCODEING = 'gbk'

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, "/manhua/{}/index.html".format(comicid))

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        name = soup.h1.text.strip()
        div = soup.find('div', {'class': 'detailInfo'})
        author = ''
        tag_name = ''
        for li in div.ul.find_all('li'):
            text = li.text.strip()
            if '作者：' in text:
                author = text.replace('作者：', '').strip()
            elif '类别：' in text:
                tag_name = text.replace('类别：', '').strip()
        desc = soup.find('div', {'id': 'intro1'}).text.strip()
        cover_image_url = soup.find('div', {'class': 'info_cover'}).img.get('src')
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       source_url=self.source_url)
        li_list = soup.find('div', {'id': 'play_0'}).ul.find_all('li')
        for chapter_number, li in enumerate(reversed(li_list), start=1):
            href = li.a.get('href')
            title = li.a.text.strip()
            url = urljoin(self.SITE_INDEX, href)
            book.add_chapter(chapter_number=chapter_number,
                             source_url=url,
                             title=title)
        if tag_name:
            book.add_tag(tag=tag_name, name=tag_name)
        return book

    def get_chapter_image_urls(self, citem):
        html = self.get_html(citem.source_url)
        packed = re.search(r'packed="(.*?)"', html).group(1)
        s = base64.b64decode(packed.encode()).decode()
        js_str = jsbeautifier.beautify(s)
        image_urls = []
        prefix = 'http://res.img.fffmanhua.com'
        for idx, url in re.findall(r'photosr\[(\d+)\] = "(.*?)";', js_str):
            image_urls.append(urljoin(prefix, url))
        return image_urls

    def get_tags(self):
        tags = self.new_tags_item()
        for tag_name, tag_id in [
            ('少年热血', 'shaonianrexue'),
            ('少女热情', 'shaonvaiqing'),
            ('武侠格斗', 'wuxiagedou'),
            ('科幻魔幻', 'kehuan'),
            ('竞技体育', 'jingjitiyu'),
            ('耽美BL', 'danmeirensheng'),
            ('侦探推理', 'zhentantuili'),
            ('恐怖灵异', 'kongbulingyi'),
        ]:
            category = '分类列表'
            tags.add_tag(category=category, name=tag_name, tag=tag_id)
        return tags

    def get_tag_result(self, tag, page=1):
        url = urljoin(self.SITE_INDEX, '/kongbulingyi/')
        if page >= 2:
            url += 'index_%s.html' % page
        soup = self.get_soup(url)
        result = self.new_search_result_item()
        for li in soup.find('div', {'id': 'dmList'}).ul.find_all('li'):
            href = li.a.get('href')
            comicid = self.get_comicid_by_url(href)
            name = li.img.get('alt')
            cover_image_url = li.img.get('_src') or li.img.get('src')
            source_url = self.get_source_url(comicid)
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

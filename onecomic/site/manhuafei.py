import json
import re
import logging
from urllib.parse import urljoin

import lzstring

from ..crawlerbase import CrawlerBase

logger = logging.getLogger(__name__)


class ManhuafeiCrawler(CrawlerBase):

    SITE = "manhuafei"
    SITE_INDEX = 'https://www.manhuafei.com/'
    SOURCE_NAME = "漫画飞"
    LOGIN_URL = SITE_INDEX

    DEFAULT_COMICID = 'mh28112'
    DEFAULT_SEARCH_NAME = '和'
    DEFAULT_TAG = "0"
    COMICID_PATTERN = re.compile(r'/manhua/(mh\d+)\.html')

    @property
    def source_url(self):
        return self.get_source_url(self.comicid)

    def get_source_url(self, comicid):
        return urljoin(self.SITE_INDEX, "/manhua/{}.html".format(comicid))

    def get_comicbook_item(self):
        soup = self.get_soup(self.source_url)
        name = soup.h1.text.strip()
        author = ''
        tags = []
        status = ''
        for i in soup.find_all('p', {'class': 'fd-list'}):
            try:
                text = i.span.text.strip()
                if '状态：' in text:
                    status = text.replace('状态：', '').strip()
                elif '类型：' in text:
                    for a in i.span.find_all('a'):
                        tag_name = a.text.strip()
                        tag = a.get('href').split('')[-1].replace('.html', '')
                        tags.append((tag_name, tag))
                elif '作者：' in text:
                    author = text
            except Exception:
                logger.info('ManhuafeiCrawler error. parse span error')
                continue
        desc = soup.find('p', {'class': 'fd-list vod-jj'}).span.text.strip()
        cover_image_url = soup.find('div', {'class': 'film-detail-img'}).img.get('src')
        book = self.new_comicbook_item(name=name,
                                       desc=desc,
                                       status=status,
                                       cover_image_url=cover_image_url,
                                       author=author,
                                       source_url=self.source_url)
        for tag_name, tag in tags:
            book.add_tag(name=tag_name, tag=tag)
        items = soup.find('div', {'class': 'all-box'}).find_all('a', {'class': 'links-of-books fixed-a-es'})
        for chapter_number, item in enumerate(reversed(items), start=1):
            url = item.get('href')
            title = item.text.strip()
            book.add_chapter(chapter_number=chapter_number,
                             source_url=url,
                             title=title)
        return book

    def get_chapter_image_urls(self, citem):
        html, soup = self.get_html_and_soup(citem.source_url)
        s = re.search(r'let img_data = "(.*?)"', html).group(1)
        domain = soup.find('div', {'class': 'vg-r-data'}).get('data-chapter-domain')
        imgs = lzstring.LZString.decompressFromBase64(s).split(',')
        image_urls = [urljoin(domain, "/uploads/" + img) for img in imgs]
        return image_urls

    def latest(self, page=1):
        if page == 1:
            url = urljoin(self.SITE_INDEX, "/update.html")
        else:
            url = urljoin(self.SITE_INDEX, "/update-page-%s.html" % page)
        soup = self.get_soup(url)
        return self.parse_book_list(soup)

    def get_tags(self):
        url = urljoin(self.SITE_INDEX, '/list.html')
        soup = self.get_soup(url)
        tags = self.new_tags_item()
        for div in soup.find_all('div', {'class': 'all-box'}):
            category = div.parent.span.text.replace('：', '').strip()
            for a in div.find_all('a'):
                name = a.text.strip()
                href = a.get('href')
                if '地区' == category:
                    group_idx = 1
                    prefix = 'a_'
                elif '类型' == category:
                    group_idx = 2
                    prefix = 'c_'
                elif '受众' == category:
                    group_idx = 3
                    prefix = 't_'
                elif '年份' == category:
                    group_idx = 4
                    prefix = 'y_'
                elif '字母' == category:
                    group_idx = 5
                    prefix = 'i_'
                elif '进度' == category:
                    group_idx = 6
                    prefix = 'm_'
                else:
                    continue
                s = href.split('/')[-1]
                tag = re.search(r'a-(\d+)-c-(\d+)-t-(\d+)-y-(.*?)-i-(.*?)-m-(\d+)\.html', s).group(group_idx)
                tags.add_tag(category=category, name=name, tag=prefix + tag)
        return tags

    def parse_book_list(self, soup):
        result = self.new_search_result_item()
        for li in soup.find('ul', {'class': 'fn-clear'}).find_all('li'):
            href = li.a.get('href')
            comicid = self.get_comicid_by_url(href)
            source_url = urljoin(self.SITE_INDEX, href)
            cover_image_url = li.a.img.get('data-original') or li.a.img.get('src')
            name = li.a.get('title')
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

    def get_tag_result(self, tag, page=1):
        params = {
            'a': '0',
            'c': '0',
            't': '0',
            'y': '0',
            'i': '0',
            'm': '0',
            'page': page
        }
        for t in tag.split(','):
            key = t.split('_')[0]
            value = t.split('_')[-1]
            params[key] = value
        url = urljoin(self.SITE_INDEX, '/list/a-{a}-c-{c}-t-{t}-y-{y}-i-{i}-m-{m}-page-{page}.html'.format(**params))
        soup = self.get_soup(url)
        return self.parse_book_list(soup)

    def search(self, name, page=1, size=None):
        url = urljoin(self.SITE_INDEX, '/search.html?q=%s&page=%s' % (name, page))
        soup = self.get_soup(url)
        result = self.new_search_result_item()
        for li in soup.find('ul', {'class': 'serach-ul'}).find_all('li'):
            href = li.a.get('href')
            comicid = self.get_comicid_by_url(href)
            source_url = urljoin(self.SITE_INDEX, href)
            cover_image_url = li.a.img.get('data-original') or li.a.img.get('src')
            name = li.a.get('title')
            result.add_result(comicid=comicid,
                              name=name,
                              cover_image_url=cover_image_url,
                              source_url=source_url)
        return result

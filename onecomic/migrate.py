import os
import re
import logging

from .comicbook import ComicBook

logger = logging.getLogger(__name__)


def migrate_image_name_format(comicbook_dir):
    """
    迁移脚本 将文件夹内的图片名从 1.jpg 2.jpg ...
    重命名为 001.jpg 002.jpg ...
    """
    for crawler_cls in ComicBook.CRAWLER_CLS_MAP.values():
        if crawler_cls.SINGLE_CHAPTER:
            # 站点目录
            dir1 = os.path.join(comicbook_dir, crawler_cls.SOURCE_NAME)
            for name1 in os.listdir(dir1):
                # 漫画目录
                dir2 = os.path.join(dir1, name1)
                if not os.path.isdir(dir2):
                    continue
                for name2 in os.listdir(dir2):
                    # 章节目录
                    dir3 = os.path.join(dir2, name2)
                    if not os.path.isdir(dir3):
                        continue

                    for image_name in os.listdir(dir3):
                        r = re.search(r'(\d+)\.(jpg|webp|gif|png|jpeg)', image_name)
                        if not r:
                            continue
                        idx, ext = r.groups()
                        image_path = os.path.join(dir3, image_name)
                        new_image_name = "{:>03}.{}".format(idx, ext)
                        if new_image_name == image_name:
                            continue
                        target_path = os.path.join(dir3, new_image_name)
                        logger.info('rename image. image=%s new_image=%s', image_path, target_path)
                        os.rename(image_path, target_path)

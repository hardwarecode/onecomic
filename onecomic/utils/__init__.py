import time
import os
import logging
import zipfile
import shutil

from PIL import Image

logger = logging.getLogger(__name__)


def safe_filename(filename=None, dirname=None, replace=' '):
    """文件名过滤非法字符串
    """
    if filename:
        illegal_str = r'\/:*?"<>|'
        replace_illegal_str = str.maketrans(illegal_str, replace * len(illegal_str))
        new_filename = filename.translate(replace_illegal_str)[:200].strip()
        if new_filename:
            return new_filename
        raise Exception('文件名不合法. new_filename={}'.format(new_filename))
    if dirname:
        illegal_str = r'\/:*?"<>|.'
        replace_illegal_str = str.maketrans(illegal_str, replace * len(illegal_str))
        new_dirname = dirname.translate(replace_illegal_str)[:200].strip()
        if new_dirname:
            return new_dirname
        raise Exception('文件名不合法. new_dirname={}'.format(new_dirname))


def get_current_time_str():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def parser_chapter_str(chapter_str, last_chapter_number=None, is_all=None):
    """将字符串描述的区间转化为一个一个数字
    :param str chapter: 类似 1-10,20-30,66 这样的字符串
    :return list number_list: [1, 2, 3, 4, ...]
    """
    if is_all:
        return list(range(1, last_chapter_number + 1))

    try:
        chapter_number = int(chapter_str)
        if chapter_number < 0:
            chapter_number = last_chapter_number + chapter_number + 1
        return [chapter_number, ]
    except ValueError:
        pass

    chapter_numbers = set()
    for block in chapter_str.split(','):
        if '-' in block:
            start, end = block.split('-', 1)
            start, end = int(start), int(end)
            for number in range(start, end + 1):
                chapter_numbers.add(number)
        else:
            number = int(block)
            chapter_numbers.add(number)
    return sorted(chapter_numbers)


def find_all_image(img_dir, sort_by=None):
    def _sort_by(x):
        return int(x.split('.')[0])
    sort_by = sort_by or _sort_by
    if not os.path.exists(img_dir):
        return []
    allow_image_suffix = ('jpg', 'jpeg', 'png', 'gif', 'webp')
    img_path_list = sorted(os.listdir(img_dir), key=sort_by)
    img_path_list = list(filter(lambda x: x.lower() not in allow_image_suffix, img_path_list))
    img_path_list = [os.path.join(img_dir, i)for i in img_path_list]
    return img_path_list


def ensure_file_dir_exists(filepath=None, dirpath=None):
    if filepath and isinstance(filepath, str):
        file_dir = os.path.dirname(filepath)
        if file_dir and not os.path.exists(file_dir):
            os.makedirs(file_dir, exist_ok=True)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)


def image_dir_to_single_image(img_dir, output_dir, sort_by=None, quality=None, max_height=None):
    quality = quality or 95
    max_height = max_height or 65500
    assert max_height <= 65500, '图片最大高度不能超过65500'

    img_path_list = find_all_image(img_dir=img_dir, sort_by=sort_by)
    img_list = [Image.open(i) for i in img_path_list]
    if not img_list:
        return output_dir
    width = img_list[0].size[0]

    # 图片太大 先分组
    group = 0
    imgs_group = [dict(width=width, height=0, imgs=[])]
    for img in img_list:
        if imgs_group[group]['height'] + img.size[1] >= max_height:
            group += 1
            imgs_group.append(dict(width=width, height=0, imgs=[]))
        imgs_group[group]['imgs'].append(img)
        imgs_group[group]['height'] += img.size[1]

    for idx, item in enumerate(imgs_group, start=1):
        width = item['width']
        height = item['height']
        new_img = Image.new('RGB', (width, height))
        current_h = 0
        img_path = os.path.join(output_dir, '%s.jpg' % idx)
        for img in item['imgs']:
            new_img.paste(img, box=(0, current_h))
            current_h += img.size[1]
        new_img.save(img_path, quality=quality)
    return output_dir


def image_dir_to_zipfile(img_dir, target_path):
    f = zipfile.ZipFile(target_path, 'w', zipfile.ZIP_DEFLATED)
    arc_basename = os.path.basename(img_dir.rstrip('/'))
    for dirpath, dirnames, filenames in os.walk(img_dir):
        for filename in filenames:
            f.write(os.path.join(dirpath, filename), arcname=os.path.join(arc_basename, filename))
    f.close()
    return target_path


def merge_books(chapter_dirs, output_dir):
    idx = 1
    for chapter_dir in chapter_dirs:
        for image in find_all_image(chapter_dir):
            ext = image.split('.')[-1]
            target_path = os.path.join(output_dir, f'{idx}.{ext}')
            shutil.copy(image, target_path)
            idx += 1


def merge_zip_books(chapter_dirs, target_path):
    arc_basename = os.path.basename(target_path)
    f = zipfile.ZipFile(target_path, 'w', zipfile.ZIP_DEFLATED)
    idx = 1
    for chapter_dir in chapter_dirs:
        for image in find_all_image(chapter_dir):
            ext = image.split('.')[-1]
            filename = f'{idx}.{ext}'
            f.write(image, arcname=os.path.join(arc_basename, filename))
            idx += 1
    f.close()
    return target_path

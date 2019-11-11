import os
import re
from werkzeug.utils import secure_filename
from PyPDF2 import PdfFileReader, PdfFileWriter
from wand.image import Image
from io import BytesIO
from pypinyin import lazy_pinyin
from utils import gen_random_str

# 封面图片所在的目录
IMAGE_PATH = './static/images/'
# 电子书所在的目录
EBOOKS_PATH = './static/ebooks/'
# 默认图片宽度
IMG_WIDTH = 400
# 默认空白封面图片
BLANK_COVER_IMAGE = './assets/blank.png'


'''
获取所有图书封面图片列表
'''


def get_cover_list():
    images_list = []
    for folderName, subfolders, filenames in os.walk(IMAGE_PATH):
        images_list.extend(filenames)
    return images_list


'''
获取图书列表
'''


def get_books(category='', keyword=''):
    images_list = get_cover_list()

    books = []
    for image in images_list:

        # 如果不是png图片，滤掉
        if not re.search(r'\.png$', image):
            continue

        image_name_parse = image.split('+', 1)
        book_category = image_name_parse[0]
        book_pure_name = image_name_parse[1].split('.png', 1)[0]

        # 如果传递了category参数，就过滤掉其他电子书，只保留当前分类
        if category and category != book_category:
            continue

        # 如果传递了keyword参数，就过滤掉其他电子书，只保留当前搜索词相关的
        if keyword and image.lower().find(keyword.lower()) == -1:
            continue

        books.append({
            'category': book_category,
            'cover': '/static/images/' + image,
            'path': '/static/ebooks/' + book_category + '/' + book_pure_name + '.pdf',
            'name': book_pure_name + '.pdf'
        })

    return books


'''
获取图书分类列表
'''


def get_categories():
    categories = []
    for foldername, subfolders, filenames in os.walk(EBOOKS_PATH):
        # 返回第一层子文件夹
        if not len(categories):
            categories = subfolders
    return categories


'''
存储图书
'''


def save_book(category, file):
    filename = secure_filename(''.join(lazy_pinyin(file.filename)))
    to_save_file = EBOOKS_PATH + category + '/' + filename
    print(to_save_file)
    if os.path.exists(to_save_file):
        print(to_save_file, '已存在')
        filename = gen_random_str(6) + '_' + filename
        to_save_file = EBOOKS_PATH + category + '/' + filename

    file.save(to_save_file)

    # 存储好pdf文件之后，需要生成对应的封面图片
    file_tuple = os.path.splitext(filename)
    nosuffix_name = file_tuple[0]

    # 把封面图片命名为'分类-书名.png'的格式
    cover_image_name = f'{category}+{nosuffix_name}'
    gen_cover_image(to_save_file, cover_image_name)


'''
新增图书分类
'''


def add_category(category):
    category_path = EBOOKS_PATH + category
    print(category_path)
    if not os.path.exists(category_path):
        os.makedirs(category_path)
    return True


'''
生成封面图片
'''


def gen_cover_image(file_path, file_name):
    # 如果输出目录不存在，则创建目录
    if not os.path.exists(IMAGE_PATH):
        os.makedirs(IMAGE_PATH)
    img_path = f'{IMAGE_PATH}{file_name}.png'

    try:
        # 截图生成封面图片，不成功就生成空白图片
        pdf_file = PdfFileReader(file_path)

        # 获取封面
        cover = pdf_file.getPage(0)
        cover_pdf = PdfFileWriter()
        cover_pdf.addPage(cover)

        # 创建二进制IO流
        cover_bytes = BytesIO()
        # 把封面写到IO流中
        cover_pdf.write(cover_bytes)
        # 返回流开头
        cover_bytes.seek(0)

        with Image(file=cover_bytes, resolution=200) as img:
            img.format = 'png'

            # 压缩图片大小
            size = img.size
            w = size[0]
            h = size[1]
            if w > h:
                img.crop(int(w / 2), 0, w, h)
                w = int(w / 2)
            img.resize(IMG_WIDTH, int(IMG_WIDTH * h / w))
            img.compression_quality = 35

            img.save(filename=img_path)
            print(f"{file_path} -> \033[1;32;40m{img_path}\033[0m")
    except Exception as e:
        print('生成封面截图失败：', e, '。改为生成简易空白占位图片')
        with Image(filename=BLANK_COVER_IMAGE) as img:
            img.save(filename=img_path)

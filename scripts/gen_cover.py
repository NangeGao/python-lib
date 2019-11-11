from PyPDF2 import PdfFileReader, PdfFileWriter
from wand.image import Image
from io import BytesIO
import os

# 电子书存储目录
EBOOKS_DIRECTORY = './static/ebooks/'
# 封面图存储目录
IMAGES_DIRECTORY = './static/images'
# 默认图片宽度
IMG_WIDTH = 400
# 默认空白封面图片
BLANK_COVER_IMAGE = './assets/blank.png'


# 生成封面图片
def gen_cover_image(file_path, file_name):
    # 如果输出目录不存在，则创建目录
    if not os.path.exists(IMAGES_DIRECTORY):
        os.makedirs(IMAGES_DIRECTORY)
    img_path = f'{IMAGES_DIRECTORY}/{file_name}.png'

    try:
        pdf_file = PdfFileReader(file_path)

        # 获取封面
        pages = pdf_file.getNumPages()
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
        print(f'\033[1;31;40m{file_path}生成封面截图失败，改为生成简易空白占位图片 -> {e} \033[0m ')
        with Image(filename=BLANK_COVER_IMAGE) as img:
            img.save(filename=img_path)


def walk_dir(directory):
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            # 获取电子书的分类
            folder_list = foldername.split('/')
            category = folder_list[len(folder_list) - 1]

            # 获取电子书名，不包含pdf后缀
            file_tuple = os.path.splitext(filename)
            nosuffix_name = file_tuple[0]
            suffix = file_tuple[1]
            if suffix != '.pdf':
                continue

            # 把封面图片命名为'分类-书名.png'的格式
            cover_image_name = f'{category}+{nosuffix_name}'

            file_path = f'{foldername}/{filename}'
            # print(f'路径是：{foldername}/{filename}')
            try:
                gen_cover_image(file_path, cover_image_name)
            except FileNotFoundError:
                print(f'{file_path}不存在！！！')
            except Exception as e:
                print(f'{file_path}发生错误： \033[1;31;40m{e}\033[0m ，没有截图成功！！！')


if __name__ == '__main__':
    walk_dir(EBOOKS_DIRECTORY)

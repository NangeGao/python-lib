import os
import re  # 正则表达式
from flask import Flask, g, request, render_template, url_for, redirect
import model
from flask_bootstrap import Bootstrap
import logging


# flask_WTF
from flask_wtf import FlaskForm
from wtforms import TextField, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed


# 上传表单
class UploadForm(FlaskForm):
    category = SelectField('分类', validators=[DataRequired()])
    file = FileField('要上传的文件', validators=[
        FileRequired(),
        FileAllowed(['pdf'], '目前只支持上传pdf格式的电子书')
    ])
    submit = SubmitField('提交')


# 新增分类表单
class AddCategoryForm(FlaskForm):
    category = TextField('新增分类名称', validators=[DataRequired()])
    submit = SubmitField('确定')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'veryHardToGuessStrings1!2@3#4$5%6^7&8*9(0)'
bootstrap = Bootstrap(app)

# Jinja2全局函数
@app.template_global()
def get_books_count():
    return len(model.get_books())

# Request Hook 请求钩子
@app.after_request
def app_after_request(response):
    if request.endpoint == 'static':
        if re.match(r'/static/styles/', request.path):
            response.cache_control.max_age = 0
        else:
            response.cache_control.max_age = 86400 * 100
    return response


# 统一的404处理页面
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


# 首页
@app.route('/')
def index():
    books = model.get_books()
    categories = model.get_categories()
    return render_template('index.html', books=books, categories=categories)


# 类别
@app.route('/category/<cate>')
def category(cate):
    books = model.get_books(category=cate)
    categories = model.get_categories()
    return render_template('index.html', books=books, categories=categories, query_category=cate)


# 搜索action
@app.route('/search/')
def search2():
    print('搜索request.args', request.args)
    keyword = request.args['keyword']
    return redirect(f'/search/{keyword}')


# 搜索
@app.route('/search/<keyword>')
def search(keyword):
    books = model.get_books(keyword=keyword)
    categories = model.get_categories()
    return render_template('index.html', books=books, categories=categories, query_keyword=keyword)


# 上传
@app.route('/upload/', methods=['GET', 'POST'])
@app.route('/upload/<preset_category>', methods=['GET', 'POST'])
def upload(preset_category=None):
    if preset_category is None:
        preset_category = ''
    field_category = None
    field_file = None
    form = UploadForm()

    # 默认选中
    default_option = ''

    # 获取分类列表
    categories = model.get_categories()
    categories_tuple = [('', '请选择分类')]
    for cate in categories:
        if cate == preset_category:
            default_option = cate
        categories_tuple.append((cate, cate))
    form.category.choices = categories_tuple

    if form.validate_on_submit():
        field_category = form.category.data
        field_file = form.file.data
        model.save_book(field_category, field_file)
        return redirect(f'/category/{field_category}')

    form.category.data = default_option

    return render_template('upload.html', form=form)


# 新增分类
@app.route('/add-category/', methods=['GET', 'POST'])
def add_category():
    field_category = None
    form = AddCategoryForm()
    if form.validate_on_submit():
        field_category = form.category.data
        model.add_category(field_category)
        return redirect(f'/upload/{field_category}')
    return render_template('category-form.html', form=form)


if __name__ == '__main__':
  app.run(host='0.0.0.0', port='8000', debug=True)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


# Simple E-Books Library

> 实践Python Flask，不写一句JavaScript

## Features

- 收录pdf电子书
- 分类查看
- 搜索
- 上传

## Involved Tech Details

- Python基础：列表、字典、元组、函数、类等
- Python Flask框架（类似Koa之于Node.js，核心功能小而美，插件机制）
- 虚拟环境隔离
- 服务端渲染 + Jinja2模板
- 路由管理
- 装饰器
- Flask-WTF处理表单
- 文件操作
- pdf读取及截图
- 异常处理
- 日志输出

## Develop

1. 安装Python 3
2. clone repo
3. 创建虚拟环境，`python -m venv venv`；
   激活，`source venv/bin/activate`
4. 初始化已有图书，`sh init.sh`
5. 启动服务，`python manage.py` 

workers = 2
threads = 2
bind = '127.0.0.1:8000'
accesslog = './log/gunicorn_access.log'
errorlog = './log/gunicorn_error.log'
loglevel = 'info'

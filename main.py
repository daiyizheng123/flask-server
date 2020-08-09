#!/usr/bin/env python3
# encoding: utf-8
'''
@author: daiyizheng: (C) Copyright 2017-2019, Personal exclusive right.
@contact: 387942239@qq.com
@software: tool
@application:@file: main.py
@time: 2020/7/30 下午12:37
@desc:
'''


from flask_cors import CORS
from flask import Flask
from views import qa
from flask import Response
app = Flask(__name__)
CORS(app)

app.register_blueprint(qa, url_prefix='/qa')





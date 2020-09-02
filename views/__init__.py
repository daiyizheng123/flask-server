#!/usr/bin/env python3
# encoding: utf-8
'''
@author: daiyizheng: (C) Copyright 2017-2019, Personal exclusive right.
@contact: 387942239@qq.com
@software: tool
@application:@file: __init__.py.py
@time: 2020/8/9 下午6:41
@desc:
'''
from flask import Blueprint
from flask_restful import Api


qa = Blueprint('qa', __name__)
api = Api(qa)

from .aq_view import *
from .ccks_qa import *

api.add_resource(QASystemOnMedicalKG, '/medical/qa', endpoint='QASystemOnMedicalKG')
api.add_resource(Nlpcc2016QA, '/nlpcc2016/qa', endpoint='NLPCC2016QA')

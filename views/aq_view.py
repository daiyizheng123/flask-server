#!/usr/bin/env python3
# encoding: utf-8
'''
@author: daiyizheng: (C) Copyright 2017-2019, Personal exclusive right.
@contact: 387942239@qq.com
@software: tool
@application:@file: aq_view.py
@time: 2020/8/9 下午6:41
@desc:
'''

from flask_restful import Resource
from flask_cors import cross_origin
from flask_restful.reqparse import RequestParser ## 校验器
from QASystemOnMedicalKG.chatbot_graph import ChatBotGraph
from logger import get_logger

logger = get_logger("log/log.log")
handler = ChatBotGraph()

class QASystemOnMedicalKG(Resource):
    parser = RequestParser()
    parser.add_argument('question', type=str, required= True, help='Rate cannot be converted')
    def get(self):
        return {"answer": "answer"}

    @cross_origin()
    def post(self):
        try:
            args = self.parser.parse_args()
            question = args.get('question')
            answer = handler.chat_main(question)
            return {"data":{"answer":answer}, "code":200, "msg":"success"}
        except Exception as e:
            logger.error(str(e))
            return {"code":5000, "msg":"failed"}



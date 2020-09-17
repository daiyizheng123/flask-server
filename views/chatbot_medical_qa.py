#!/usr/bin/env python3
# encoding: utf-8
'''
@author: daiyizheng: (C) Copyright 2017-2019, Personal exclusive right.
@contact: 387942239@qq.com
@software: tool
@application:@file: chatbot_medical_qa.py
@time: 2020/9/2 下午2:35
@desc:
'''
from flask_restful import Resource
from flask_cors import cross_origin
from flask_restful.reqparse import RequestParser ## 校验器
from logger import get_logger

from QASystemOnMedicalKGDL.chatbot_graph import ChatBotGraph

logger = get_logger("log/log.log")

class chatboatMedicalQa(Resource):
    """
    基于深度学习医疗问答系统
    """
    parser = RequestParser()
    parser.add_argument('question', type=str, required=True, help='Rate cannot be converted')
    def get(self):

        return {"question": "answer"}

    @cross_origin()
    def post(self):
        try:
            args = self.parser.parse_args()
            question = args.get('question')
            chat = ChatBotGraph()
            answer = chat.chat_main(question)
            return {"data":{"answer":answer},"code":200, "msg":"success"}
        except Exception as e:
            logger.error(str(e))
            return {"code":5000, "msg":"failed"}
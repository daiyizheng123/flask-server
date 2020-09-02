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
# from mysqlUtils import MysqlClinet
# import random
# from NLPCC2016QA.nlpccUtils import NLPCCQA
logger = get_logger("log/log.log")
handler = ChatBotGraph()
# ner_model = NLPCCQA()


# @qa.route("/", methods=['POST'])
# def QASystemOnMedicalKG():
#     try:
#         question = request.json.get('question')
#         print(question)
#         answer = handler.chat_main(question)
#         return jsonify({"data":{"answer":answer}, "code":200, "msg":"success"})
#     except Exception as e:
#         print(e)
#         return jsonify({ "code":5000, "msg":"failed"})


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

# class Nlpcc2016QA(Resource):
#
#     def get(self):
#         sql = "SELECT question FROM nlpcc_qa where  id=%d" %(random.randint(1, 14600))
#         sql_res = MysqlClinet().query(sql)
#         return {"question": sql_res[0][0]}
#
#     @cross_origin()
#     def post(self):
#         try:
#             sql_res = []
#             while len(sql_res)==0:
#                 sql = "SELECT question FROM nlpcc_qa where  id=%d" % (random.randint(1, 14600))
#                 sql_res = MysqlClinet().query(sql)
#             ret = ner_model.nlpccQA(sql_res[0][0])
#             return {"data":{"answer":ret},"code":200, "msg":"success"}
#         except Exception as e:
#             logger.error(str(e))
#             return {"code":5000, "msg":"failed"}


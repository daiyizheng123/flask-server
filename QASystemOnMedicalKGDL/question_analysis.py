#!/usr/bin/env python3
# encoding: utf-8
'''
@author: daiyizheng: (C) Copyright 2017-2019, Personal exclusive right.
@contact: 387942239@qq.com
@software: tool
@application:@file: question_analysis.py
@time: 2020/9/8 上午10:48
@desc:
'''
import requests
from settings import MODEL_HTTP_IP_PORT
import os
class question_ays:
    def __init__(self):

        # ['E-dis', 'B-sym', 'B-che', 'E-dru', 'I-che', 'E-che', 'E-sym', 'I-dis', 'S', 'I-sym', 'B-dis', 'I-dru','B-dru']
        self.state2entityType={'dis':'disease', 'sym':'symptom', 'dru':'drug', 'che':"check"}

    def analysis(self,text):
        # {'args': {'发烧': ['symptom'], '流鼻涕': ['symptom']}, 'question_types': ['symptom_curway']}
        res = {}
        args={}
        question_types=[]
        ## NER

        url_ner = MODEL_HTTP_IP_PORT + "chatbotBERT"
        data = {"text": text}
        res_ner = requests.post(url_ner, data).json()
        new_text = text
        for r_dict in res_ner:
            for r in r_dict.get("info", []):
                begin = r["begin"]
                end = r['end']
                words = r['words']
                words_type = r['type']
                if args.get(words, ""):
                    args[words].append(self.state2entityType[words_type])
                else:
                    args[words] = [self.state2entityType[words_type]]
                new_text = new_text[:end+1] + self.state2entityType[words_type] + new_text[end+1:]

        ## classify
        """
        classify = self.classifyApp.questionClassify(new_text) #2 symptom_disease
        """
        url_classify = MODEL_HTTP_IP_PORT + "chatbotMedicalQAClassify"
        res_class = requests.post(url_classify, data).json()
        classify = ""
        for c in res_class:
            classify = c.get("classify", "")

        question_types.append(classify)
        res['args'] = args
        res['question_types'] = question_types
        return res


if __name__=="__main__":
    ques = question_ays()
    text="我发烧流鼻涕怎么治疗"
    while(text!="" and text!=" "):
        text=input("请输入一句话：")
        if text == "quit" or text=="" or text == " ":break
        res=ques.analysis(text)
        print(res)



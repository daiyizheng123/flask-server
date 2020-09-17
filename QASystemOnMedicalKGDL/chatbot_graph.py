# coding: utf-8


#from question_classifier import *
from .question_parser import *
from .answer_search import *
from .question_analysis import *

'''问答类'''
class ChatBotGraph:
    def __init__(self):
        #self.classifier = QuestionClassifier()
        self.classifier = question_ays()
        self.parser = QuestionPaser()
        self.searcher = AnswerSearcher()

    def chat_main(self, sent):
        answer = '您的问题我还不能理解，请换个问法'
        res_classify = self.classifier.analysis(sent)
        if not res_classify:
            return answer
        res_sql = self.parser.parser_main(res_classify)
        final_answers = self.searcher.search_main(res_sql)
        if not final_answers:
            return answer
        else:
            return '\n'.join(final_answers)



#!/usr/bin/env python3
# encoding: utf-8
'''
@author: daiyizheng: (C) Copyright 2017-2019, Personal exclusive right.
@contact: 387942239@qq.com
@software: tool
@application:@file: nlpccUtils.py
@time: 2020/9/2 上午9:27
@desc:
'''

from NLPCC2016QA.BERT_CRF import BertCrf
from transformers import BertTokenizer, BertConfig, BertForSequenceClassification
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler, TensorDataset
import torch
import pymysql
import os
import code
from tqdm import tqdm, trange
from mysqlUtils import MysqlClinet


class SimInputFeatures(object):

    def __init__(self, input_ids, attention_mask, token_type_ids, label = None):
        self.input_ids = input_ids
        self.attention_mask = attention_mask
        self.token_type_ids = token_type_ids
        self.label = label

class NLPCCQA():
    root_path = os.path.abspath(os.path.dirname(__file__))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    CRF_LABELS = ["O", "B-LOC", "I-LOC"]
    SIM_LABELS = ["0", "1"]
    def __init__(self, max_length=64):
        self.max_length = max_length
        tokenizer_inputs = ()
        tokenizer_kwards = {'do_lower_case': False,
                            'max_len': max_length,
                            'vocab_file': self.root_path + '/bert_base_chinese/bert-base-chinese-vocab.txt'}

        self.tokenizer = BertTokenizer(*tokenizer_inputs, **tokenizer_kwards)

        self.ner_model = self.get_ner_model(config_file=self.root_path + '/bert_base_chinese/bert-base-chinese-config.json',
                                       pre_train_model=self.root_path + '/bert_base_chinese/best_ner.bin',
                                       label_num=len(self.CRF_LABELS))
        self.ner_model = self.ner_model.to(self.device)

        self.sim_model = self.get_sim_model(config_file=self.root_path + '/bert_base_chinese/bert-base-chinese-config.json',
                                       pre_train_model=self.root_path + '/bert_base_chinese/best_sim.bin',
                                       label_num=len(self.SIM_LABELS))
        self.sim_model = self.sim_model.to(self.device)

    def get_ner_model(self, config_file, pre_train_model, label_num=2):
        model = BertCrf(config_name=config_file, num_tags=label_num, batch_first=True)
        model.load_state_dict(torch.load(pre_train_model))
        return model.to(self.device)


    def get_sim_model(self, config_file, pre_train_model, label_num=2):
        bert_config = BertConfig.from_pretrained(config_file)
        bert_config.num_labels = label_num
        model = BertForSequenceClassification(bert_config)
        model.load_state_dict(torch.load(pre_train_model))
        return model


    def get_entity(self, model, tokenizer, sentence, max_len=64):
        pad_token = 0
        sentence_list = list(sentence.strip().replace(' ', ''))
        text = " ".join(sentence_list)
        inputs = tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=max_len,
            truncation_strategy='longest_first'  # We're truncating the first sequence in priority if True
        )

        input_ids, token_type_ids = inputs["input_ids"], inputs["token_type_ids"]
        attention_mask = [1] * len(input_ids)  # [1,1,1,....]
        padding_length = max_len - len(input_ids)  #

        # padding
        input_ids = input_ids + ([pad_token] * padding_length)
        attention_mask = attention_mask + ([0] * padding_length)
        token_type_ids = token_type_ids + ([0] * padding_length)
        labels_ids = None

        assert len(input_ids) == max_len, "Error with input length {} vs {}".format(len(input_ids), max_len)
        assert len(attention_mask) == max_len, "Error with input length {} vs {}".format(len(attention_mask), max_len)
        assert len(token_type_ids) == max_len, "Error with input length {} vs {}".format(len(token_type_ids), max_len)

        input_ids = torch.tensor(input_ids).reshape(1, -1).to(self.device)
        attention_mask = torch.tensor(attention_mask).reshape(1, -1).to(self.device)
        token_type_ids = torch.tensor(token_type_ids).reshape(1, -1).to(self.device)
        labels_ids = labels_ids

        model = model.to(self.device)
        model.eval()
        ret = model(input_ids=input_ids,
                    tags=labels_ids,
                    attention_mask=attention_mask,
                    token_type_ids=token_type_ids)

        pre_tag = ret[1][0]
        assert len(pre_tag) == len(sentence_list) or len(pre_tag) == max_len - 2

        pre_tag_len = len(pre_tag)
        b_loc_idx = self.CRF_LABELS.index('B-LOC')
        i_loc_idx = self.CRF_LABELS.index('I-LOC')
        o_idx = self.CRF_LABELS.index('O')

        if b_loc_idx not in pre_tag and i_loc_idx not in pre_tag:
            print("没有在句子[{}]中发现实体".format(sentence))
            return ''
        if b_loc_idx in pre_tag:

            entity_start_idx = pre_tag.index(b_loc_idx)
        else:

            entity_start_idx = pre_tag.index(i_loc_idx)
        entity_list = []
        entity_list.append(sentence_list[entity_start_idx])
        for i in range(entity_start_idx + 1, pre_tag_len):
            if pre_tag[i] == i_loc_idx:
                entity_list.append(sentence_list[i])
            else:
                break

        return entity_list


    def semantic_matching(self, model, tokenizer, question, attribute_list, answer_list, max_length):
        assert len(attribute_list) == len(answer_list)

        pad_token = 0
        pad_token_segment_id = 1
        features = []
        for (ex_index, attribute) in enumerate(attribute_list):  # 此循环是 0,国籍     1,事迹 进行循环
            inputs = tokenizer.encode_plus(
                text=question,
                text_pair=attribute,
                add_special_tokens=True,
                max_length=max_length,
                truncation_strategy='longest_first'
            )

            input_ids, token_type_ids = inputs["input_ids"], inputs["token_type_ids"]
            attention_mask = [1] * len(input_ids)

            padding_length = max_length - len(input_ids)
            input_ids = input_ids + ([pad_token] * padding_length)
            attention_mask = attention_mask + ([0] * padding_length)
            token_type_ids = token_type_ids + ([pad_token_segment_id] * padding_length)

            assert len(input_ids) == max_length, "Error with input length {} vs {}".format(len(input_ids), max_length)
            assert len(attention_mask) == max_length, "Error with input length {} vs {}".format(len(attention_mask),
                                                                                                max_length)
            assert len(token_type_ids) == max_length, "Error with input length {} vs {}".format(len(token_type_ids),
                                                                                                max_length)
            features.append(
                SimInputFeatures(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
            )
        all_input_ids = torch.tensor([f.input_ids for f in features], dtype=torch.long)
        all_attention_mask = torch.tensor([f.attention_mask for f in features], dtype=torch.long)
        all_token_type_ids = torch.tensor([f.token_type_ids for f in features], dtype=torch.long)
        dataset = TensorDataset(all_input_ids, all_attention_mask, all_token_type_ids)
        sampler = SequentialSampler(dataset)
        dataloader = DataLoader(dataset, sampler=sampler, batch_size=128)

        all_logits = None
        for batch in tqdm(dataloader, desc="Best Attribute"):
            model.eval()
            batch = tuple(t.to(self.device) for t in batch)
            with torch.no_grad():
                inputs = {'input_ids': batch[0],
                          'attention_mask': batch[1],
                          'token_type_ids': batch[2],
                          'labels': None
                          }
                outputs = model(**inputs)
                logits = outputs[0]
                logits = logits.softmax(dim=-1)

                if all_logits is None:
                    all_logits = logits.clone()
                else:
                    all_logits = torch.cat([all_logits, logits], dim=0)
        pre_rest = all_logits.argmax(dim=-1)
        if 0 == pre_rest.sum():
            return torch.tensor(-1)
        else:
            return pre_rest.argmax(dim=-1)


    def select_database(self, sql):
        # connect database
        try:
            conn = MysqlClinet()
            results = conn.query(sql)
        except:
            results = []
        return results

    # 文字直接匹配，看看属性的词语在不在句子之中
    def text_match(self, attribute_list, answer_list, sentence):
        assert len(attribute_list) == len(answer_list)
        idx = -1
        for i, attribute in enumerate(attribute_list):
            if attribute in sentence:
                idx = i
                break
        if -1 != idx:
            return attribute_list[idx], answer_list[idx]
        else:
            return "", ""


    def nlpccQA(self, sent):
        #
        messages = {"question": sent, "subject":[], "relation":[], "object":[]}
        entity_list = self.get_entity(model=self.ner_model, tokenizer=self.tokenizer, sentence=sent, max_len=self.max_length)

        if 0 == len(entity_list):
            print("未发现实体")
            return messages

        entity = "".join(entity_list)
        messages['subject'] = [entity]
        sql_str = 'select * from nlpccQA where entity = "{}"'.format(entity)

        triple_list = self.select_database(sql_str)
        triple_list = list(triple_list)
        if 0 == len(triple_list):
            print("未找到 {} 相关信息".format(entity))
            return messages
        triple_list = list(zip(*triple_list))
        print("triple_list:", triple_list)
        attribute_list = triple_list[1]
        answer_list = triple_list[2]

        attribute, answer = self.text_match(attribute_list, answer_list, sent)  #

        if attribute != '' and answer != '':
            ret = "直接匹配出来：{}的{}是{}".format(entity, attribute, answer)
            messages['relation'] = [attribute]
            messages['object'] = [answer]
        else:
            attribute_idx = self.semantic_matching(self.sim_model, self.tokenizer, sent, attribute_list, answer_list, self.max_length).item()
            # code.interact(local = locals())
            if -1 == attribute_idx:
                ret = ''
            else:
                attribute = attribute_list[attribute_idx]
                answer = answer_list[attribute_idx]
                ret = "语义匹配：{}的{}是{}".format(entity, attribute, answer)
                messages['relation'] = [attribute]
                messages['object'] = [answer]
        if '' == ret:
            print("未找到{}相关信息".format(entity))
        else:
            print(ret)
        return messages


if __name__ == '__main__':
    sent = "我想知道戴维斯是什么国家的人"
    # sent = "你知道因为有你是谁的作的曲吗？"
    # sent = "陈刚哪里人"
    # sent = "神雕侠侣是什么类型"
    # sent = "李鑫别名"
    # sent = "王磊生辰"
    # sent = "西游记作者的"
    a = NLPCCQA()
    b = a.nlpccQA(sent)
    print(b)
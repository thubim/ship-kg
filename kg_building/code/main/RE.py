import os
import re

import sys
os.chdir(os.path.dirname(__file__))
sys.path.append("..")
from core.nlp import NLP
from core.extractor import Extractor

def extract_item(origin_sentence):
    prefixItem = ""
    sub_len = 0
    first_num_cnt = 0
    first_dot_cnt = 0
    for i in range(len(origin_sentence)):
        c = origin_sentence[i]
        if c.isalpha():
            sub_len = i
            break;
        if c.isspace():
            continue
        prefixItem += c
        if c.isdigit():
            first_num_cnt += 1
        elif c == '.':
            first_dot_cnt += 1

    item_level = 4
    if first_dot_cnt > 0 and first_num_cnt + first_dot_cnt == len(prefixItem):
        item_level = 1
    elif "(" in prefixItem or ")" in prefixItem:
        item_level = 2
    elif first_num_cnt + first_dot_cnt > 0:
        item_level = 3
    sentence = origin_sentence[sub_len:]
    return item_level, prefixItem, sentence

if __name__ == '__main__':
    input_path = '../../data/input_text2.txt'          # 输入的文本文件
    output_path = '../../data/knowledge_triple.json'  # 输出的处理结果Json文件

    if os.path.isfile(output_path):
        os.remove(output_path)
    # os.mkdir(output_path)

    print('Start extracting...')

    # NLP(分词，词性标注，命名实体识别，依存句法分析)
    nlp = NLP()
    num = 1  # 关系知识三元组

    recordItem = [] # 前缀条目记录
    prevItem = ""   # 上一条前缀条目记录

    with open(input_path, 'r', encoding='utf-8') as f_in:
        # 预处理
        sentence_tmp = f_in.read().replace(' ', '').replace('􀆰', '.').replace('ꎻ', '；').replace('ꎬ', '，').replace('ꎮ', '。')
        # 分句，获得句子列表
        origin_sentences = re.split('[。？！；]|\n', sentence_tmp)
        # 遍历每一篇文档中的句子
        pos_list = []
        for origin_sentence in origin_sentences:
            # 原始句子长度小于2，跳过
            if (len(origin_sentence) <= 2):
                continue
            print('*****')
            # print(origin_sentence)

            # 提取前缀条目信息
            item_level, prefixItem, processed_sentence = extract_item(origin_sentence)
            while recordItem and recordItem[-1][0] >= item_level:
                recordItem.pop()

            sen_item = ""
            if item_level == 1:
                sen_item = prefixItem
            elif item_level == 2:
                if len(recordItem) >= 1:
                    sen_item = recordItem[-1][1] + " " + prefixItem
                else:
                    sen_item = prefixItem
            elif item_level == 3:
                if len(recordItem) >= 2:
                    sen_item = recordItem[-2][1] + " " + recordItem[-1][1] + " " + prefixItem
                elif len(recordItem) >= 1:
                    sen_item = recordItem[-1][1] + " " + prefixItem
                else:
                    sen_item = prefixItem
            elif item_level == 4:
                sen_item = prevItem
            else:
                sen_item = prefixItem
            prevItem = sen_item
            if item_level != 4:
                recordItem.append((item_level, prefixItem))

            # 分词处理 jieba分词工具
            lemmas = nlp.segment(processed_sentence)
            # 词性标注 ltp
            words_postag = nlp.postag(lemmas)
            # 命名实体识别 ltp
            words_netag = nlp.netag(words_postag)
            #for word in words_netag:
            #    if word.postag not in pos_list:
            #        pos_list.append(word.postag)
            #    print(word.to_string())
            # 依存句法分析 ltp
            sentence = nlp.parse(words_netag)
            print(sentence.to_string())

            extractor = Extractor()
            num = extractor.extract(processed_sentence, sentence, output_path, num, sen_item)
        #print(pos_list)

import os
import re
import json
import sys
import csv
from numpy.core.records import array
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")))
from core.nlp import NLP
from tool.append_to_json import AppendToJson

def old_main_run():
    kn_path = '../../data/lexicon.json'
    spec_path = '../../data/规范原文.json'
    output_path = "../../data/spec.json"
    kn_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), kn_path))
    spec_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), spec_path))
    output_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), output_path))

    if os.path.isfile(output_path):
        os.remove(output_path)
    # os.mkdir(output_path)

    print('Start renew_spec...')

    kn_lines = open(kn_path, 'r', encoding='utf-8').readlines()
    print(len(kn_lines))
    kn_dic = dict()
    for i, line in enumerate(kn_lines):
        line = json.loads(line)
        arrays = line['关系']
        name1 = arrays[2]
        name2 = arrays[3]
        offset1 = arrays[4]
        offset2 = arrays[5]
        type1 = arrays[6]
        type2 = arrays[7]
        content = line['句子']
        if content not in kn_dic.keys():
            kn_dic[content] = []
        name_off1 = name1 + "&" + offset1 + "&" + type1
        name_off2 = name2 + "&" + offset2 + "&" + type2
        if name_off1 not in kn_dic[content]:
            kn_dic[content].append(name_off1)
        if name_off2 not in kn_dic[content]:
            kn_dic[content].append(name_off2)

    spec_lines = open(spec_path, 'r', encoding='utf-8').readlines()
    print(len(spec_lines))
    cnt = 0
    notempty_cnt = 0
    for i, line in enumerate(spec_lines):
        cnt += 1
        line = json.loads(line)
        _id = line["id"]
        _spec = line["spec"]
        _item = line['item']
        _content = line["content"]
        _word_list = []
        if _content in kn_dic.keys():
            _word_list = kn_dic[_content]
        if len(_word_list) == 0:
            notempty_cnt += 1
        AppendToJson().append(output_path, {"id": _id, "spec": _spec, "item": _item, "content": _content, "words": _word_list})
    print(cnt, notempty_cnt)
    print("renew_spec End......")


def main_run():
    spec_path = '../../data/规范原文.json'
    output_path = "../../data/spec.json"
    lexicon_path = '../../resource/use_lexicon.csv'
    spec_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), spec_path))
    output_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), output_path))
    lexicon_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), lexicon_path))
    
    if os.path.isfile(output_path):
        os.remove(output_path)
    # os.mkdir(output_path)
    
    print('Start renew_spec...')
    
    lexicon_list = []
    with open(lexicon_path, "r", encoding='utf-8', errors='ignore') as f:
        reader = csv.reader((line.replace('\0','') for line in f))
        for item in reader:
            num = reader.line_num - 1
            if num == 0:
                continue
            lexicon_list.append(item[0])
    
    spec_lines = open(spec_path, 'r', encoding='utf-8').readlines()
    print(len(spec_lines))

    nlp = NLP()
    
    cnt = 0
    notempty_cnt = 0
    for i, line in enumerate(spec_lines):
        cnt += 1
        line = json.loads(line)
        _id = line["id"]
        _spec = line["spec"]
        _item = line['item']
        _content = line["content"]
        _word_list = []
        _offset_list = []
        
        # 分词处理 jieba分词工具
        lemmas = nlp.segment(_content)
        # 词性标注 ltp
        words_postag = nlp.postag(lemmas)
        
        for word in words_postag:
            word_postag = word.get_postag()
            word_type = word.get_type()
            word_lemma = word.get_lemma()
            word_offset = word.get_offset()
            if word_postag in  {'n', 'ns', 'ni', 'nh', 'nz', 'j', 'nl', 'r'} and word_lemma in lexicon_list:
                _word_list.append(word_lemma)
                _offset_list.append(word_offset)
        
        if len(_word_list) == 0:
            notempty_cnt += 1
        AppendToJson().append(output_path, {"id": _id, "spec": _spec, "item": _item, "content": _content, "words": _word_list, "offset": _offset_list})
        
    print(cnt, notempty_cnt)
    print("renew_spec End......")
    
if __name__ == '__main__':
    main_run()

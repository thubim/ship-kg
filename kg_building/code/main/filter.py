import os
import re
import json
import sys
import csv

from matplotlib.pyplot import flag
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")))
from tool.append_to_json import AppendToJson

def main_run():
    input_path = '../../data/knowledge_triple.json'
    output_path = '../../data/lexicon.json'
    lexicon_path = '../../resource/final_lexicon.csv'
    out_dict_path = '../../resource/use_lexicon.csv'
    input_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), input_path))
    output_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), output_path))
    lexicon_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), lexicon_path))
    out_dict_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), out_dict_path))
    
    if os.path.isfile(output_path):
        os.remove(output_path)
    # os.mkdir(output_path)
    
    print('Start filtering...')
    
    lexicon_list = []
    with open(lexicon_path, "r", encoding='utf-8', errors='ignore') as f:
        reader = csv.reader((line.replace('\0','') for line in f))
        for item in reader:
            num = reader.line_num - 1
            if num == 0:
                continue
            lexicon_list.append(item[0])
    
    # 方位对应关系
    pos_dict = {
        "上": "上方",
        "高": "上方",
        "下": "下方",
        "低": "下方",
        "底": "下方",
        "前": "前方",
        "后": "后方",
        "中": "内部",
        "间": "内部",
        "内": "内部",
        "外": "外部",
        "侧": "侧边",
        "平行": "平行",
        "穿": "穿越",
        "经过": "穿越",
        "邻": "邻接",
        "处": "位于",
        "位于": "位于",
        "的": "位于"
    }
    
    delete_item_list = ["1.1.2.19", "1.2.1.7", "1.3.1.2", "1.3.2.7", "2.13.1.1", "2.23.1.1", "3.5.1.1", "3.6.2.2", "3.7.4.1"]
    delete_id_list = ["1415", "1416"]
    
    use_dict_set = set()
    
    lines = open(input_path, 'r', encoding='utf-8').readlines()
    print(len(lines))
    forbidden_list = ["册", "篇", "章", "本节", "部分", "要求", "规定", "支持"]
    for i, line in enumerate(lines):
        line = json.loads(line)
        sen = line["句子"]
        sen_id = line["编号"]
        sen_item = line["条目"]
        confs = line['置信度']
        rel_conf = float(confs[0].strip())
        if_then_conf = float(confs[1].strip())
        arrays = line['关系']
        rel = arrays[0].strip()
        if_then = arrays[1].strip()
        name1 = arrays[2].strip()
        name2 = arrays[3].strip()
        offset1 = str(arrays[4].strip())
        offset2 = str(arrays[5].strip())
        type1 = arrays[6].strip()
        type2 = arrays[7].strip()
        if rel == "" or if_then == "" or name1 == "" or name2 == "":
            continue
        
        flag = False
        for word in forbidden_list:
            if word in name1 or word in name2:
                flag = True
        if flag:
            continue
        
        if rel == "包含" and (sen_id in delete_id_list or sen_item in delete_item_list):
            continue
        
        if rel_conf < 0.98:
            continue
        
        # 添加方位附加信息
        add_info = ""
        if rel == "方位":
            bias = 5
            sen_tmp = sen.split(" ")[1]
            offset1 = int(offset1)
            offset2 = int(offset2)
            left1 = offset1 - bias if offset1 - bias >= 0 else 0
            right1 = offset1 + len(name1) + bias if offset1 + len(name1) + bias < len(sen_tmp) else len(sen_tmp)
            left2 = offset2 - bias if offset2 - bias >= 0 else 0
            right2 = offset2 + len(name2) + bias if offset2 + len(name2) + bias < len(sen_tmp) else len(sen_tmp)
            tocheck_sen = sen_tmp[left2:right2]
            tocheck_sen = tocheck_sen.replace(name2, "").replace(name1, "")
            for pos in pos_dict.keys():
                if pos in tocheck_sen:
                    add_info = pos_dict[pos]
                    break
            if add_info == "":
                tocheck_sen = sen_tmp[left1:right1]
                tocheck_sen = tocheck_sen.replace(name2, "").replace(name1, "")
                for pos in pos_dict.keys():
                    if pos in sen_tmp[left1:right1]:
                        add_info = pos_dict[pos]
                        break
        if add_info == "":
            add_info = rel
        line["add_info"] = add_info
        
        # "制约": [("施工", "施工"), ("属性", "施工"), ("施工", "成果"), ("属性", "成果"), ("进程", "施工"), ("属性", "属性")],
        zy_list = [("属性", "施工"), ("属性", "成果"), ("属性", "属性")]
        if rel == "制约":
            if (type1, type2) in zy_list:
                continue
        
        triple = name1 + "&" + name2 + "&" + str(offset1) + "&" + str(offset2) + "&" + type1 + "&" + type2
        if name1 in lexicon_list and name2 in lexicon_list:
            AppendToJson().append(output_path, line)
            use_dict_set.add(name1 + "&" + type1)
            use_dict_set.add(name2 + "&" + type2)
            # print(triple)
        else:
            # print("[不匹配] - " + triple)
            pass
    
    with open(out_dict_path, "w+") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["lexicon", "label"])
        for dict_pair in use_dict_set:
            name = dict_pair.split("&")[0]
            type = dict_pair.split("&")[1]
            writer.writerow([name, type])
    
    print("filter Ending...")

if __name__ == '__main__':
    main_run()
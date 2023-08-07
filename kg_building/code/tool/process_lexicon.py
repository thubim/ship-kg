# -*- coding: utf-8 -*-

import os
import sys

def get_lexicon(input_path, output_path,):
    """
    Args:
        input_path: string, 待处理词典文件
        output_path: string, 存储处理后的词典文件
    """
    words = ''
    with open(input_path, 'r', encoding='utf-8') as fin, \
        open(output_path, 'a', encoding='utf-8') as fout:

        for line in fin:
            seg = line.strip('\r\n').split('\t')
            word = seg[0]
            words += word + '\n'

        fout.write(words)
        fout.flush()
        fin.close()
        fout.close()

def process1():
    input_path = '../../resource/THUOCL_law.txt'  # 清华大学开放中文词库(法律)
    output_path = '../../resource/THUOCL_law_lexicon.txt'  # 存储处理后的词典文件
    # 删除已存在的词典文件并重新创建
    if os.path.exists(output_path) and os.path.isfile(output_path):
        os.remove(output_path)
        # os.mknod(output_path)

    get_lexicon(input_path, output_path)

if __name__ == '__main__':
    in_path = "../../data/完整专业分类/" # 概念关系 专业分类 实验
    out_path = "../../resource/"
    filels = os.listdir(in_path)
    for file in filels:
        if file != ".DS_Store":
            print("==== " + file)
            outfile = open(out_path + file, 'w+')
            lines = open(in_path + file, 'r', encoding='utf-8').readlines()
            name_list = []
            for i, line in enumerate(lines):
                line = line.strip()
                if line == "":
                    continue
                print(line)
                line = line.split(" ")
                name1 = line[0]
                name2 = line[2]
                print(name1)
                print(name2)
                if name1 not in name_list:
                    name_list.append(name1)
                    outfile.write(name1 + "\n")
                if name2 not in name_list:
                    name_list.append(name2)
                    outfile.write(name2 + "\n")
            outfile.close()












# -*- coding: utf-8 -*-

# from django.http import HttpResponse
import os
import json
import time
import numpy as np
import requests
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, JsonResponse, response
from py2neo import Graph, Node, Relationship, database
from django.core import serializers
from functools import cmp_to_key
from django.views.decorators import csrf
from kg_building.code.main import buildSpecFromRawText, extract_main, filter, filter_repeat, renew_spec
from neo4jGraph import write2neo4j
import csv

DEBUG = True #True

test_graph = Graph(
    "http://127.0.0.1:7474",
    username="neo4j",
    password="neo4j"
)

def f2(a, b):
    return b['val'] - a['val']

def f3(a, b):
    return b['val'] - a['val']

def near(request):
    return render(request, 'near.html')

def find_near_before(request):
    a = request.GET['pname']

    # maxn = request.GET['maxnear']

    data = test_graph.run("Match (n:Entity{name: $str})-[r:REL]-(end:Entity) return r.value, "
                           "n.name,end.name,n.tid order by r.value desc", str=a).data()

    for i in range(0, len(data)):
        for j in range(i + 1, len(data)):
            if (data[i]['n.name'] == data[j]['end.name'] and data[i]['end.name'] == data[j]['n.name']) or \
                    (data[i]['n.name'] == data[j]['n.name'] and data[i]['end.name'] == data[j]['end.name']):
                data[i]['r.value'] += data[j]['r.value']
                data.remove(data[j])
                break

    # mydata = {}
    # for i in range(0,len(data)):
    #    if mydata.has_key(data[i]['n.tid']):
    #       mydata[data[i]['n.tid']]['data'].append({"name":data[i]['end.name'],"val":data[i]['r.value']})
    #   else:
    #      mydata[data[i]['n.tid']] = {}
    #     mydata[data[i]['n.tid']]['data']  = []

    # for item in mydata:
    #    mydata[item]['count'] = len(mydata[item]['data'])
    #    mydata[item]['data'].sort(key=cmp_to_key(f2))
    mydata = []
    help = {}
    cnt = 0
    for i in range(0, len(data)):
        if help.has_key(data[i]['n.tid']):
            mydata[help[data[i]['n.tid']]]['data'].append({'name': data[i]['end.name'], 'val': data[i]['r.value']})
        else:
            mydata.append({'tid': data[i]['n.tid'], 'data': []})
            help[data[i]['n.tid']] = cnt
            cnt += 1
    for i in range(0, len(mydata)):
        mydata[i]['count'] = len(mydata[i]['data'])
    for i in range(0, len(mydata)):
        mydata[i]['data'].sort(key=cmp_to_key(f2))

    mydata.sort(key=cmp_to_key(f3))

    response = HttpResponse(json.dumps(mydata), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response

def pic(request):
    return render(request, 'near.html')

def get_had_node(name):
    path = "../kg_building/data/same_word.json"
    path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), path))
    
    same_list = []
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            line = json.loads(line)
            same_list.append(line["same_word"])
    
    replace_dict = {}
    for wl in same_list:
        wl_len = len(wl)
        for i in range(1, wl_len):
            replace_dict[wl[i]] = wl[0]
    
    origin_name = name
    for word in replace_dict.keys():
        if word == name:
            name = replace_dict[word]
    
    res_list = []
    for i in range(len(same_list)):
        if origin_name in same_list[i]:
            res_list = same_list[i]
            break
    
    return origin_name, name, res_list

def find_pic(request):
    name = request.GET['name']
    
    input_path = "../kg_building/data/lexicon_pic.json"
    input_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), input_path))
    
    origin_name, name, words_list = get_had_node(name)
    
    data = ""
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            line = json.loads(line)
            if name == line['word']:
                data = line
                break
    
    data = {"replace_name": name, "res": data}
    response = HttpResponse(json.dumps(data), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response

def get_node_relation(name):
    data = test_graph.run("Match (n:Entity{name: $str})-[r:REL]->(end:Entity) return r.value, r.rel, r.if_then, r.add_info, r.rel_color, r.rel_group, r.item, r.spec, r.triple, r.content, "
                            "n.name,end.name order by r.value desc", str=name).data()
    
    reverse_data = test_graph.run("Match (n:Entity)-[r:REL]->(end:Entity{name: $str}) return r.value, r.rel, r.if_then, r.add_info, r.rel_color, r.rel_group, r.item, r.spec, r.triple, r.content, "
                            "n.name,end.name order by r.value desc", str=name).data()
    res_list = {}
    for i in range(0, len(data)):
        data[i]['dir'] = "1"
        if data[i]['end.name'] not in res_list.keys():
            res_list[data[i]['end.name']] = []
        res_list[data[i]['end.name']].append(data[i])

    for i in range(0, len(reverse_data)):
        reverse_data[i]['dir'] = "2"
        reverse_data[i]['end.name'] = reverse_data[i]['n.name']
        reverse_data[i]['n.name'] = name
        if reverse_data[i]['end.name'] not in res_list.keys():
            res_list[reverse_data[i]['end.name']] = []
        res_list[reverse_data[i]['end.name']].append(reverse_data[i])

    res = []
    index = 0
    for key in res_list.keys():
        ls = res_list[key]
        res.append(ls[0])
        res[index]["all"] = 1
        if len(ls) > 1:
            res[index]['all'] = res[index]['all'] + 1
            res[index]['r.value'] = str(res[index]['r.value']) + "@@@" + str(ls[1]['r.value'])
            res[index]['r.rel_group'] = str(res[index]['r.rel_group']) + "@@@" + str(ls[1]['r.rel_group'])
            res[index]['r.rel_color'] = str(res[index]['r.rel_color']) + "###" + str(ls[1]['r.rel_color'])
            res[index]['r.rel'] += "###" + ls[1]['r.rel']
            res[index]['r.if_then'] += "###" + ls[1]['r.if_then']
            res[index]['r.add_info'] += "###" + ls[1]['r.add_info']
            res[index]['r.item'] += "###" + ls[1]['r.item']
            res[index]['r.spec'] += "###" + ls[1]['r.spec']
            res[index]['r.triple'] += "###" + ls[1]['r.triple']
            res[index]['r.content'] += "###" + ls[1]['r.content']
            res[index]['dir'] += "@@@" + ls[1]['dir']
        index += 1
    return res

def find_near(request):
    request_name = request.GET['pname']
    maxn = request.GET['maxnear']
    
    print(request_name, maxn)
    
    origin_name, request_name, words_list = get_had_node(request_name)

    data = get_node_relation(request_name)

    '''
    have_list = []
    for i in range(0, len(data)):
        if i in have_list:
            continue
        for j in range(i + 1, len(data)):
            if j in have_list:
                continue
            if (data[i]['n.name'] == data[j]['end.name'] and data[i]['end.name'] == data[j]['n.name']) or \
                    (data[i]['n.name'] == data[j]['n.name'] and data[i]['end.name'] == data[j]['end.name']):
                have_list.append(j)

    data = [data[i] for i in range(0, len(data)) if i not in have_list]
    '''

    node_list = [request_name]
    node_cnt = 0
    for i in range(0, len(data)):
        if data[i]['end.name'] not in node_list:
            node_list.append(data[i]['end.name'])
            node_cnt += 1
            if node_cnt >= int(maxn):
                break

    data_tmp = []
    for i in range(0, len(data)):
        if data[i]['end.name'] in node_list:
            data_tmp.append(data[i])
    data = data_tmp

    last_index = min(int(maxn), len(data))
    data = data[:last_index]
    
    if (request.GET['mr'] == "1"):
        data = {"replace_name": request_name, "same_list": words_list, "res": data}
        response = HttpResponse(json.dumps(data), content_type="application/json")
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "*"
        return response
    # tdata = []
    # for i in range(0,maxn):
    #    tdata[i] = data[i]

    # data = tdata
    '''
    for i in data:
        iname = i['end.name']
        #inode = test_graph.node(i['end.id'])
        for j in data:
            jname = j['end.name']
            if iname==jname:
                continue
            #jnode = test_graph.node(j['end.id'])
            #find_r = test_graph.match_one(start_node=inode,end_node=jnode,bidirectional=True);
            find_r = test_graph.data("Match (n:Entity{name: {i}})-[r:REL]-(end:Entity{name:{j}}) return r.value",i=iname
                                     ,j=jname)
            if find_r:
                data.append({"r.value":find_r[0]['r.value'],"n.name":iname,"end.name":jname})
    '''
    '''
    for i in range(0, len(data)):
        hisdata = test_graph.data(
            "Match (n:Entity{name: {str}})-[r:REL]-(end:Entity) where r.value > 10 return r.value, "
            "n.name,end.name order by r.value desc limit 25", str=data[i]['end.name'])
        for j in range(0, len(hisdata)):
            if hisdata[j]['end.name'] == data[i]['end.name']:
                data.append(hisdata[j])
    '''
    hisdatas = []
    for i in range(0, len(data)):
        hisdata = get_node_relation(data[i]['end.name'])
        hisdatas.append(hisdata)

    have_dic = {}
    for i in range(0, len(data)):
        edgestr1 = data[i]['end.name'] + "&" + data[i]['n.name']
        edgestr2 = data[i]['n.name'] + "&" + data[i]['end.name']
        have_dic[edgestr1] = data[i]['r.value']
        have_dic[edgestr2] = data[i]['r.value']
    
    for i in range(0, len(data)):
        for j in range(0, len(hisdatas)):
            for k in range(0, len(hisdatas[j])):
                if data[i]['end.name'] == hisdatas[j][k]['end.name']:
                    innerval = hisdatas[j][k]['r.value']
                    edgestr1 = hisdatas[j][k]['end.name'] + "&" + hisdatas[j][k]['n.name']
                    edgestr2 = hisdatas[j][k]['n.name'] + "&" + hisdatas[j][k]['end.name']
                    if (edgestr1 not in have_dic.keys()) and (edgestr2 not in have_dic.keys()):
                        have_dic[edgestr1] = innerval
                        have_dic[edgestr2] = innerval
                    else:
                        continue
                    if hisdatas[j][k] in data:
                        continue
                    else:
                        data.append({'r.value': innerval, 'r.rel': hisdatas[j][k]['r.rel'], 'r.if_then': hisdatas[j][k]['r.if_then'], 'r.add_info': hisdatas[j][k]['r.add_info'],'r.rel_color': hisdatas[j][k]['r.rel_color'], 'r.rel_group': hisdatas[j][k]['r.rel_group'], 'r.content': hisdatas[j][k]['r.content'], 'r.item':hisdatas[j][k]["r.item"], 'r.spec':hisdatas[j][k]["r.spec"], 'r.triple':hisdatas[j][k]["r.triple"], 'n.name': hisdatas[j][k]['end.name'], 'end.name': hisdatas[j][k]['n.name'], 'dir': hisdatas[j][k]['dir'], 'all': hisdatas[j][k]['all']})
    
    data = {"replace_name": request_name, "same_list": words_list, "res": data}
    response = HttpResponse(json.dumps(data), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response


def path(request):
    return render(request, 'path.html')


def find_path(request):
    # return render(request,'path.html')
    fname = request.GET['fname']
    tname = request.GET['tname']
    
    print(fname, tname)
    
    origin_fname, fname, words_flist = get_had_node(fname)
    origin_tname, tname, words_tlist = get_had_node(tname)
    
    data = test_graph.run("Match(p1:Entity{name:$fp}),(p2:Entity{name:$tp}),p=allshortestpaths((p1)-[*..20]->(p2)) "
                          "return p", fp=fname, tp=tname).data()

    if DEBUG:
        print(data)

    if not data:
        data = []
        data = {"replace_fname": fname, "replace_tname": tname, "same_flist": words_flist, "same_tlist": words_tlist, "res": data}
        response = HttpResponse(json.dumps(data), content_type="application/json")
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "*"
        return response
    nodes_total = []
    rels_total = []
    # all_nodes_total = []
    paths = []
    cnt = 0
    for datai in data:
        nodes = datai['p'].nodes
        rels = datai['p'].relationships
        this_path = []
        this_path_val = 0
        this_path_values = []
        for i in range(0, len(nodes)):
            # all_nodes_total.append(nodes[i]['name'])
            if nodes[i]['name'] not in nodes_total:
                nodes_total.append(nodes[i]['name'])
            if i < len(nodes) - 1:
                values = test_graph.run("Match (n:Entity{name: $fp})-[r:REL]->(end:Entity{name: $tp}) return r.value, r.rel, r.if_then, r.add_info, r.rel_color, r.rel_group",
                                        fp=nodes[i]['name'], tp=nodes[i + 1]['name']).data()
                rel_val = values[0]['r.value']
                rel_rel = values[0]['r.rel']
                rel_if_then = values[0]['r.if_then']
                add_info = values[0]['r.add_info']
                rel_color = values[0]['r.rel_color']
                rel_group = values[0]['r.rel_group']
                rels_total.append(
                    {"start_node": nodes[i]['name'], "end_node": nodes[i + 1]['name'], "val": rel_val, "rel": rel_rel, "if_then": rel_if_then, "add_info": add_info, "rel_color": rel_color, "rel_group": rel_group})
                this_path.append(
                    {"start_node": nodes[i]['name'], "end_node": nodes[i + 1]['name'], "val": rel_val, "rel": rel_rel, "if_then": rel_if_then, "add_info": add_info, "rel_color": rel_color, "rel_group": rel_group})
                this_path_val += rel_val
                this_path_values.append(rel_val)
        paths.append({'path': this_path, 'val': int(np.sum(this_path_values))})
    paths.sort(key=cmp_to_key(f2))

    if DEBUG:
        print(nodes_total)
        print(rels_total)
        print(paths)
    # 双保险
    total_rep = [nodes_total, rels_total, paths]
    data = {"replace_fname": fname, "replace_tname": tname, "same_flist": words_flist, "same_tlist": words_tlist, "res": total_rep}
    response = HttpResponse(json.dumps(data), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response


def is_friends(request):
    fperson = request.GET['fname']
    tperson = request.GET['tname']
    data = test_graph.run("Match (n:Entity{name: $str1})-[r:REL]-(end:Entity{name:$str2}) return r.value ",
                            str1=fperson, str2=tperson).data()
    rdata = {}
    if (len(data) > 0):
        rdata['status'] = 1
    else:
        rdata['status'] = 0
    response = HttpResponse(json.dumps(rdata), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response


def getEdgeinfo(request):
    name1 = request.GET['sname']
    name2 = request.GET['tname']

    url = ""

    querystring = {"query": name1 + " " + name2, "num": "5", "start": "1"}

    headers = {
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        'upgrade-insecure-requests': "1",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'accept-encoding': "gzip, deflate",
        'accept-language': "zh-CN,zh;q=0.8",
        'cache-control': "no-cache",
        'postman-token': "5549dc28-2253-f247-d5f9-1f8e87bd830f"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    res = json.loads(response.text)
    response = HttpResponse(json.dumps(res), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response


def is_entity(request):
    fperson = request.GET['name']
    data = test_graph.run("Match (n:Entity{name: $str1}) return n.name ", str1=fperson).data()
    rdata = {}
    if (len(data) > 0):
        rdata['status'] = 1
    else:
        rdata['status'] = 0
    response = HttpResponse(json.dumps(rdata), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response

def graph(request):
    return render(request, 'graph.html')

def get_graph(request):
    data = test_graph.run("Match (n:Entity)-[r:REL]->(end:Entity) return r.value, r.rel, r.if_then, rel_color, r.rel_group, r.item, r.spec, r.triple, r.content, n.name, end.name").data()
    if not data:
        response = HttpResponse(json.dumps([]), content_type="application/json")
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "*"
        return response

    if DEBUG:
        print(len(data))
    '''
    have_list = []
    for i in range(0, len(data)):
        if i in have_list:
            continue
        for j in range(i + 1, len(data)):
            if j in have_list:
                continue
            if (data[i]['n.name'] == data[j]['end.name'] and data[i]['end.name'] == data[j]['n.name']) or \
                    (data[i]['n.name'] == data[j]['n.name'] and data[i]['end.name'] == data[j]['end.name']):
                have_list.append(j)
    data = [data[i] for i in range(0, len(data)) if i not in have_list]

    print(len(data))
    '''

    response = HttpResponse(json.dumps(data), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response

def get_spec(request):
    path = "../kg_building/data/spec.json"
    path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), path))
    lines = open(path, 'r', encoding='utf-8').readlines()
    
    if DEBUG:
        print(len(lines))
    data = []
    for i, line in enumerate(lines):
        line = json.loads(line)
        data.append(line)

    response = HttpResponse(json.dumps(data), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response

def search_spec(request):
    return render(request, 'search_spec.html')

def search_from_spec(request):
    word_name = ""
    if request.GET:
        word_name = request.GET['pname']
    
    if DEBUG:
        print(word_name)

    path = "../kg_building/data/spec.json"
    path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), path))
    lines = open(path, 'r', encoding='utf-8').readlines()
    data = []
    for i, line in enumerate(lines):
        line = json.loads(line)
        content = line['content']
        if word_name == "" or content.find(word_name) != -1:
            data.append(line)

    response = HttpResponse(json.dumps(data), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response

def add_post(request):
    return render(request, 'add_post.html')

def add_wordlist_2_lexicon(word_list, type_list):
    input_path = "../kg_building/resource/final_lexicon.csv"
    input_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), input_path))
    
    if DEBUG:
        print('Start add_word...')
    lexicon_list = []
    label_list = []
    with open(input_path, "r", encoding='utf-8', errors='ignore') as f:
        reader = csv.reader((line.replace('\0','') for line in f))
        for item in reader:
            num = reader.line_num - 1
            if num == 0:
                continue
            lexicon_list.append(item[0])
            label_list.append(item[1])
    
    if DEBUG:
        print(len(lexicon_list))
    written = False
    with open(input_path, 'a') as csvfile:
        writer = csv.writer(csvfile)
        for i in range(len(word_list)):
            word = word_list[i]
            type = type_list[i]
            if word != "" and word not in lexicon_list:
                writer.writerow([word, type])
                written = True
    
    if DEBUG:
        print(len(lexicon_list))
        print('add_word Ending...')
    return written

# global variable
progress_cnt = 0
progress_status = ""
total_cnt = 6
total_start = 0
total_time = 400
deal_flag = False
word_list = []
type_list = []

def run_whole_process(word_list, type_list):
    global progress_cnt, progress_status, total_start
    
    if DEBUG:
        print("Start whole_run...")
    total_start = time.time()
    time_start = total_start
    progress_status = "添加词汇"
    written = add_wordlist_2_lexicon(word_list, type_list)
    progress_cnt += 1
    
    if DEBUG:
        print('[add_wordlist_2_lexicon] time cost: ', time.time() - time_start, ' s')
    time_start = time.time()
    if not written:
        progress_cnt = total_cnt
        progress_status = "完成"
        
        if DEBUG:
            print("not need run whole process")
        return
    
    #buildSpecFromRawText.main_run()
    #print('[buildSpecFromRawText] time cost: ', time.time() - time_start, ' s')
    progress_status = "提取中"
    extract_main.main_run()
    progress_cnt += 1
    
    if DEBUG:
        print('[extract_main] time cost: ', time.time() - time_start, ' s')
    time_start = time.time()
    progress_status = "后处理"
    filter.main_run()
    progress_cnt += 1
    
    if DEBUG:
        print('[filter] time cost: ', time.time() - time_start, ' s')
    time_start = time.time()
    filter_repeat.main_run()
    progress_cnt += 1
    
    if DEBUG:
        print('[filter_repeat] time cost: ', time.time() - time_start, ' s')
    time_start = time.time()
    renew_spec.main_run()
    progress_cnt += 1
    
    if DEBUG:
        print('[renew_spec] time cost: ', time.time() - time_start, ' s')
    time_start = time.time()
    progress_status = "图谱生成"
    write2neo4j.main_run()
    progress_status = "完成"
    progress_cnt += 1
    
    if DEBUG:
        print('[write2neo4j] time cost: ', time.time() - time_start, ' s')
        print('[whole_run] time cost: ', time.time() - total_start, ' s')
        print("whole_run Ending...")

def run_whole_test(word_list):
    global progress_cnt, progress_status, total_start
    total_start = time.time()
    time_start = total_start
    progress_cnt = 1
    progress_status = "开始"
    
    if DEBUG:
        print(progress_cnt, progress_status, total_start, time_start)
    time.sleep(10)
    progress_cnt = total_cnt
    progress_status = "完成"
    
    if DEBUG:
        print("[test] run whole process")
        print(progress_cnt, progress_status, total_start, time_start)

def add_word_ops(request):
    global deal_flag, word_list
    word_list = []
    if request.GET:
        word_list = request.GET['add_word'].split(",")
        type_list = request.GET['add_type'].split(",")
    
    if DEBUG:
        print(word_list)
        print(type_list)
    # 打开处理开关
    deal_flag = True

    response = HttpResponse(json.dumps([]), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response

def deal_process(request):
    global deal_flag, word_list, type_list
    # 重新运行整个流程
    if deal_flag:
        deal_flag = False
        # run_whole_test(word_list)
        run_whole_process(word_list, type_list)
        word_list = []
        type_list = []
    time_diff = time.time() - total_start
    if progress_cnt == total_cnt:
        time_diff = total_time
    # return JsonResponse({"prog_status": progress_status, "prog_time": time_diff * 100 / total_time, "prog_cnt": progress_cnt * 100 / total_cnt}, safe=False)
    return JsonResponse({"prog_status": progress_status, "total_time": total_time, "time_diff": time_diff, "prog_cnt": progress_cnt, "total_cnt": total_cnt}, safe=False)

if __name__ == '__main__':
    run_whole_process()

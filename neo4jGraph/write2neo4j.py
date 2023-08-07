import os
import json
import csv
from py2neo import Graph, Node, Relationship

def build_neo4j_graph():
    # create an unique index
    neo4j_graph = Graph(
        "http://127.0.0.1:7474",
        username="neo4j",
        password="neo4j"
    )
    neo4j_graph.delete_all()
    # neo4j_graph.run("CREATE CONSTRAINT ON (cc:Entity) ASSERT cc.name IS UNIQUE")
    
    return neo4j_graph

def getxlsx(rel_path):
    with open(rel_path, "r") as csvfile:
        reader = csv.reader(csvfile)
        rel_dict = {}
        rel_group_id = 1
        for item in reader:
            if reader.line_num <= 1:
                continue
            rel = item[2]
            rel_dict[rel] = rel_group_id
            rel_group_id += 1
        return rel_dict, rel_group_id
    
def export_json_2_neo4j(neo4j_graph, path, same_path, rel_path):
    print("Start exporting...")
    rel_dict, rel_group_max_id = getxlsx(rel_path)
    
    same_list = []
    with open(same_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            line = json.loads(line)
            same_list.append(line["same_word"])
    
    replace_dict = {}
    for wl in same_list:
        wl_len = len(wl)
        for i in range(1, wl_len):
            replace_dict[wl[i]] = wl[0]
    
    triple_dic = {}
    node_dic = {}
    lines = open(path, 'r', encoding='utf-8').readlines()
    print(len(lines))
    for i, line in enumerate(lines):
        line = json.loads(line)
        arrays = line['关系']
        probs = line['置信度']
        content = line['句子']
        item = line['条目']
        spec = line["规范"]
        add_info = line["add_info"]
        rel = arrays[0].strip()
        if_then = arrays[1].strip()
        prob_rel = probs[0]
        prob_if_then = probs[1]
        name1 = arrays[2].strip()
        name2 = arrays[3].strip()
        offset1 = arrays[4].strip()
        offset2 = arrays[5].strip()
        if rel == "状态" or rel == "" or if_then == "" or name1 == "" or name2 == "":
            continue
        new_name1 = name1
        new_name2 = name2
        
        for word in replace_dict.keys():
            if word == name1:
                new_name1 = replace_dict[word]
            if word == name2:
                new_name2 = replace_dict[word]
        
        name_off1 = name1 + "&" + offset1
        name_off2 = name2 + "&" + offset2
        triple = new_name1 + "->" + new_name2
        whole_triple = name_off1 + "->" + name_off2
        if triple not in triple_dic.keys():
            if new_name1 not in node_dic.keys():
                test_node_1 = Node("Entity", name=new_name1)
                neo4j_graph.create(test_node_1)
                node_dic[new_name1] = test_node_1
            else:
                test_node_1 = node_dic[new_name1]
            if new_name2 not in node_dic.keys():
                test_node_2 = Node("Entity", name=new_name2)
                neo4j_graph.create(test_node_2)
                node_dic[new_name2] = test_node_2
            else:
                test_node_2 = node_dic[new_name2]
            node_1_call_node_2 = Relationship(test_node_1, "REL", test_node_2)
            node_1_call_node_2['value'] = 1
            rel_group_id = rel_dict[rel]
            node_1_call_node_2['rel_group'] = rel_group_id
            node_1_call_node_2['rel_color'] = str(rel_group_id)
            node_1_call_node_2['value'] = 1
            node_1_call_node_2['rel'] = rel
            node_1_call_node_2['add_info'] = add_info
            node_1_call_node_2['prob_rel'] = prob_rel
            node_1_call_node_2['if_then'] = if_then
            node_1_call_node_2['prob_if_then'] = prob_if_then
            node_1_call_node_2['content'] = content
            node_1_call_node_2['item'] = item
            node_1_call_node_2['spec'] = spec
            node_1_call_node_2['triple'] = whole_triple
            neo4j_graph.create(node_1_call_node_2)
            
            triple_dic[triple] = []
            triple_dic[triple].append(node_1_call_node_2)
            
            #print(triple)
        else:
            # 两个句子中间用"###"分割
            rel_group_id = rel_dict[rel]
            node_1_call_node_2 = triple_dic[triple][0]
            if node_1_call_node_2['rel'].split("###")[0] != rel:
                node_1_call_node_2['rel_group'] = rel_group_max_id
            node_1_call_node_2['rel_color'] += "###" + str(rel_group_id)
            node_1_call_node_2['value'] += 1
            node_1_call_node_2['rel'] += "###" + rel
            node_1_call_node_2['add_info'] += "###" + add_info
            node_1_call_node_2['prob_rel'] += "###" + prob_rel
            node_1_call_node_2['if_then'] += "###" + if_then
            node_1_call_node_2['prob_if_then'] += "###" + prob_if_then
            node_1_call_node_2['content'] += "###" + content
            node_1_call_node_2['item'] += "###" + item
            node_1_call_node_2['spec'] += "###" + spec
            node_1_call_node_2['triple'] += "###" + whole_triple
            neo4j_graph.push(node_1_call_node_2)
            #print("[重复] - " + triple)
    print("export Ending...")

def main_run():
    json_path = '../kg_building/data/lexicon.json'
    same_path = '../kg_building/data/same_word.json'
    rel_path = '../kg_building/code/deepke/data/origin/origin_rel/relation.csv'
    json_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), json_path))
    same_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), same_path))
    rel_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_path))
    neo4j_graph = build_neo4j_graph()
    export_json_2_neo4j(neo4j_graph, json_path, same_path, rel_path)

if __name__ == "__main__":
    main_run()

import os
import json
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

def export_json_2_neo4j(path, neo4j_graph):
    triple_dic = {}
    node_dic = {}

    lines = open(path, 'r', encoding='utf-8').readlines()
    print(len(lines))
    for i, line in enumerate(lines):
        if i > 1000:
            break
        line = json.loads(line)
        arrays = line['关系']
        content = line['句子']
        item = line['条目']
        name1 = arrays[0]
        relation = arrays[1].replace('：', '').replace(':', '').replace('　', '').replace(' ', '').replace('【','').replace('】', '')
        name2 = arrays[2]
        triple = name1 + "&" + name2
        reverse_triple = name2 + "&" + name1
        if (triple not in triple_dic.keys()) and (reverse_triple not in triple_dic.keys()):
            if name1 not in node_dic.keys():
                test_node_1 = Node("Entity", name=name1)
                neo4j_graph.create(test_node_1)
                node_dic[name1] = test_node_1
            else:
                test_node_1 = node_dic[name1]
            if name2 not in node_dic.keys():
                test_node_2 = Node("Entity", name=name2)
                neo4j_graph.create(test_node_2)
                node_dic[name2] = test_node_2
            else:
                test_node_2 = node_dic[name2]
            node_1_call_node_2 = Relationship(test_node_1, "REL", test_node_2)
            node_1_call_node_2['value'] = 1
            node_1_call_node_2['rel'] = relation
            node_1_call_node_2['content'] = content
            node_1_call_node_2['item'] = item
            neo4j_graph.create(node_1_call_node_2)

            node_2_call_node_1 = Relationship(test_node_2, "REL", test_node_1)
            node_2_call_node_1['value'] = 1
            node_2_call_node_1['rel'] = relation
            node_2_call_node_1['content'] = content
            node_2_call_node_1['item'] = item
            neo4j_graph.create(node_2_call_node_1)

            triple_dic[triple] = []
            triple_dic[triple].append(node_1_call_node_2)
            triple_dic[triple].append(node_2_call_node_1)

            triple_dic[reverse_triple] = []
            triple_dic[reverse_triple].append(node_1_call_node_2)
            triple_dic[reverse_triple].append(node_2_call_node_1)
            print(triple)
        else:
            node_1_call_node_2 = triple_dic[triple][0]
            node_1_call_node_2['value'] += 1
            node_1_call_node_2['rel'] += "###" + relation     # 两个句子中间用"###"分割
            node_1_call_node_2['content'] += "###" + content
            node_1_call_node_2['item'] += "###" + item
            neo4j_graph.push(node_1_call_node_2)
            node_2_call_node_1 = triple_dic[triple][1]
            node_2_call_node_1['value'] += 1
            node_2_call_node_1['rel'] += "###" + relation
            node_2_call_node_1['content'] += "###" + content
            node_2_call_node_1['item'] += "###" + item
            neo4j_graph.push(node_2_call_node_1)
            print("[重复] - " + triple)


if __name__ == "__main__":
    json_path = '../data/knowledge_triple.json'
    neo4j_graph = build_neo4j_graph()
    export_json_2_neo4j(json_path, neo4j_graph)
    print("完成")

import os
import re
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")))
from tool.append_to_json import AppendToJson

def main_run():
	lexicon_name = "lexicon"
	input_path = '../../data/' + lexicon_name + ".json"
	output_path = '../../data/' + lexicon_name + ".json"
	input_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), input_path))
	output_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), output_path))

	print('Start filter_repeat...')
	lines = open(input_path, 'r', encoding='utf-8').readlines()

	if os.path.isfile(output_path):
		os.remove(output_path)
	
	had_rel_dict = {}
	prev_data_list = []
	prev_index = 0
	prev_content = ""
	for i, line in enumerate(lines):
		line = json.loads(line)
		content = line['句子']
		if content != prev_content:
			for data in prev_data_list:
				AppendToJson().append(output_path, data)
			prev_content = content
			prev_data_list = []
			prev_index = 0
		
		arrays = line['关系']
		probs = line['置信度']
		prob_rel= float(probs[0])
		prob_if_then = float(probs[1])
		rel = arrays[0].strip()
		if_then = arrays[1].strip()
		name1 = arrays[2].strip()
		name2 = arrays[3].strip()
		offset1 = arrays[4].strip()
		offset2 = arrays[5].strip()
		if rel == "" or if_then == "" or name1 == "" or name2 == "":
			continue
		'''
		triple_rel = name1 + "&" + offset1 + "->" + rel + "->" + name2 + "&" + offset2
		triple_if_then = name1 + "&" + offset1 + "->" + if_then + "->" + name2 + "&" + offset2
		'''
		triple_rel = name1 + "->" + rel + "," + if_then + "->" + name2 
		if content not in had_rel_dict.keys():
			had_rel_dict[content] = {}
		if triple_rel not in had_rel_dict[content].keys():
			had_rel_dict[content][triple_rel] = (prob_rel, prob_if_then, prev_index)
			prev_data_list.append(line)
			prev_index += 1
			# print(triple)
		else:
			old_prob_rel = had_rel_dict[content][triple_rel][0]
			old_prob_if_then = had_rel_dict[content][triple_rel][1]
			old_index = had_rel_dict[content][triple_rel][2]
			if prob_rel > old_prob_rel or (prob_rel == old_prob_rel and prob_if_then > old_prob_if_then):
				had_rel_dict[content][triple_rel] = (prob_rel, prob_if_then, old_index)
				prev_data_list[old_index] = line
			# print("[重复] - " + triple)
	for data in prev_data_list:
		AppendToJson().append(output_path, data)
	print("filter_repeat Ending...")

if __name__ == '__main__':
	main_run()
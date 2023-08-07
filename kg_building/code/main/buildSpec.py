import os
import re
import json
import sys
os.chdir(os.path.dirname(__file__))
sys.path.append("..")
from tool.append_to_json import AppendToJson

if __name__ == '__main__':
	spec_name = "规范原文"
	input_path = '../../data/knowledge_triple.json'
	output_path = '../../data/' + spec_name + ".json"

	if os.path.isfile(output_path):
		os.remove(output_path)
	# os.mkdir(output_path)

	print('Start filtering...')

	specList = []
	lines = open(input_path, 'r', encoding='utf-8').readlines()
	reId = 0
	prevLine = ""
	print(len(lines))
	for i, line in enumerate(lines):
		line = json.loads(line)
		print(line)
		id = line["编号"]
		if id < 136:
			continue
		item = line["条目"]
		sentence = line["句子"]
		arrays = line['关系']
		name1 = arrays[0]
		name2 = arrays[2]

		if prevLine != "" and item == prevLine["条目"]:
			if sentence != prevLine["句子"]:
				specList[reId - 1]["句子"] += sentence
			if name1 not in specList[reId - 1]["关系"]:
				specList[reId - 1]["关系"].append(name1)
			if name2 not in specList[reId - 1]["关系"]:
				specList[reId - 1]["关系"].append(name2)
		else:
			specList.append({"编号": reId + 1, "条目": item, "句子": item + " " + sentence, "关系": [name1, name2]})
			reId += 1

		prevLine = line

	for spec in specList:
		AppendToJson().append(output_path, spec)



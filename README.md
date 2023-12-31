# 船舶知识图谱

## 前置依赖

1. **规范文本**

2. **词典库**

3. **neo4j数据库**

## 简单运行方法

1. 【kg_diango/kg_building/code/main/run】运行`python simple_run.py`

## 完整运行方法

1. 【kg_django/kg_building/code/main】运行`buildSpecFromRawText.py`。基于**规范文本**(`ship_text.txt`)解析，生成`规范原文.json`（包含条目和规范正文）；

2. 【kg_django/kg_building/code/main】运行`extract_main.py`。基于`规范原文.json`，进行知识图谱识别，识别出其中的实体和三元组关系，生成`knowledge_triple.json`；

3. 【kg_django/kg_building/code/main】运行`filter.py`。基于**词典库**(`resource/lexicon.csv`)，对`knowledge_triple.json`进行过滤，把不包含在词典库的关系过滤掉，生成新的`lexicon.json`；

4. 【kg_django/kg_building/code/main】运行filter_repeat.py去除`lexicon.json`中的重复内容，生成`lexicon.json`；

5. 【kg_django/kg_building/code/main】运行`renew_spec.py`。基于`规范原文.json`和`lexicon.json`，一个句子可能对应多个三元组，重新梳理，使每个句子的三元组的实体词汇都对应到相应句子中（用于网站标红），生成`spec.json`；

6. 【kg_django/neo4jGraph】运行`write2neo4j.py`。将`lexicon.json`输入到neo4j，进行知识图谱存储和生成知识图谱（有向的，`write2neo4j(undir).py`是生成无向图的，即双向的）；

7. 【kg_django/kg_django】搭建的网站，是基于在neo4j存储的知识图谱（用于知识图谱关键词搜索、路径查询及整体的显示）和`spec.json`（用于规范原文信息以及标红的显示）。



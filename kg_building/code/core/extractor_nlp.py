import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")))
from core.extract_by_nlp import ExtractByNLP
from bean.word_unit import WordUnit
from bean.sentence_unit import SentenceUnit
from bean.entity_pair import EntityPair
import torch
from hydra import utils
import deepke.models as models
import copy

class ExtractorNLP:
    """抽取生成知识三元组
    Attributes:
        entities: WordUnit list，句子的实体列表
        entity_pairs: EntityPair WordUnit list，句子实体对列表
    """
    entities = []  # 存储该句子中的可能实体
    entity_pairs = []  # 存储该句子中(满足一定条件)的可能实体对
    
    cfg_rel = None
    device_rel = None
    model_rel = None
    
    cfg_if_then = None
    device_if_then = None
    model_if_then = None
    
    def __init__(self, cfg):
        '''
        cwd = utils.get_original_cwd()
        cwd = cwd[0:-5]
        cfg.cwd = cwd
        '''
        
        self.cfg_rel, self.device_rel, self.model_rel = self.set_config(cfg, 200, 8, \
            'best_model/model_rel/2021-12-13_15-04-19/lm_epoch10.pth', \
                'data/origin/origin_rel', \
                    'data/out/out_rel')
        
        self.cfg_if_then, self.device_if_then, self.model_if_then = self.set_config(cfg, 100, 3, \
            'best_model/model_if_then/2022-01-06_13-11-06/lm_epoch5.pth', \
                'data/origin/origin_if_then', \
                    'data/out/out_if_then')
        
    
    def set_config(self, config, hidden_size, num_relations, fp, data_path, out_path):
        cfg = copy.deepcopy(config)
        cfg.cwd = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../deepke"))
        cfg.pos_size = 2 * cfg.pos_limit + 2
        
        # model
        __Model__ = {
            'cnn': models.PCNN,
            'rnn': models.BiLSTM,
            'transformer': models.Transformer,
            'gcn': models.GCN,
            'capsule': models.Capsule,
            'lm': models.LM,
        }
        
        # 最好在 cpu 上预测
        cfg.use_gpu = False
        if cfg.use_gpu and torch.cuda.is_available():
            device = torch.device('cuda', cfg.gpu_id)
        else:
            device = torch.device('cpu')
        
        cfg.hidden_size = hidden_size
        cfg.num_relations = num_relations
        cfg.fp = os.path.join(cfg.cwd, fp)
        cfg.data_path = data_path
        cfg.out_path = out_path
        model = __Model__[cfg.model_name](cfg)
        model.load(cfg.fp, device=device)
        model.to(device)
        model.eval()
        
        return cfg, device, model
    
    
    def extract(self, origin_sentence, sentence, words_netag, file_path, num, spec_info, item_info):
        """
        Args:
            origin_sentence: string，原始句子
            sentence: SentenceUnit，句子单元
        Returns:
            num： 知识三元组的数量编号
        """
        self.get_entities(words_netag)
        self.get_entity_pairs(sentence)
        
        for entity_pair in self.entity_pairs:
            entity1 = entity_pair.entity1
            entity2 = entity_pair.entity2
            
            extract_nlp = ExtractByNLP(origin_sentence, sentence, entity1, entity2, file_path, num, spec_info, item_info)
            
            extract_nlp.predict_sentence(self.cfg_rel, self.model_rel, self.device_rel, self.cfg_if_then, self.model_if_then, self.device_if_then)
            
            num = extract_nlp.num
        
        return num
    

    def get_entities(self, words_netag):
        """获取句子中的所有可能实体
        Args:
            sentence: SentenceUnit，句子单元
        Returns:
            None
        """
        self.entities.clear()  # 清空实体
        for word in words_netag:
            if self.is_entity(word):
                self.entities.append(word)

    def get_entity_pairs(self, sentence):
        """组成实体对，限制实体对之间的实体数量不能超过4
        Args:
            sentence: SentenceUnit，句子单元
        """
        self.entity_pairs.clear()  # 清空实体对
        length = len(self.entities)
        for i in range(length):
            for j in range(length):
                if i != j and self.entities[i].lemma != self.entities[j].lemma:
                #and self.get_entity_num_between(self.entities[i], self.entities[j], sentence) <= 4:
                    self.entity_pairs.append(EntityPair(self.entities[i], self.entities[j]))
        '''
        i = 0
        while i < length:
            j = i + 1
            while j < length:
                if self.entities[i].lemma != self.entities[j].lemma:
                    # and self.get_entity_num_between(self.entities[i], self.entities[j], sentence) <= 4:
                    self.entity_pairs.append(EntityPair(self.entities[i], self.entities[j]))
                j += 1
            i += 1
        '''

    def is_entity(self, entry):
        """判断词单元是否实体
        Args:
            entry: WordUnit，词单元
        Returns:
            *: bool，实体(True)，非实体(False)
        """
        # 候选实体词性列表        
        # ['nh', 'n', 'i', 'v', 'nd', 'b', 'ni', 'r', 'wp', 'ns', 'nt', 'm', 'j']
        entity_postags = {'nh', 'ni', 'ns', 'nz', 'n', 'j', 'nl', 'r'}
        if entry.postag in entity_postags:
            return True
        else:
            return False

    def get_entity_num_between(self, entity1, entity2, sentence):
        """获得两个实体之间的实体数量
        Args:
            entity1: WordUnit，实体1
            entity2: WordUnit，实体2
        Returns:
            num: int，两实体间的实体数量
        """
        if entity1.ID > entity2.ID:
            tmp = entity1
            entity1 = entity2
            entity2 = tmp
        num = 0
        i = entity1.ID + 1
        while i < entity2.ID:
            if self.is_entity(sentence.words[i]):
                num += 1
            i += 1
        return num


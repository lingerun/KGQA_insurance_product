#!/usr/bin/python3
# encoding: utf-8
# @author: lingyun
# @file: question_classifier.py
# @time: 2018/12/18 11:24
# @desc:


import pandas as pd
import ahocorasick

class QuestionClassifier:
    def __init__(self):
        data_path = 'data/ins_product_data.xls'
        data = pd.read_excel(data_path)

        company = data['公司名称']
        product = data['产品名称']
        category = data['类别1']

        self.company = list(set(company))
        self.product = list(set(product))
        self.category = list(set(category))

        #构造actree
        self.region_words = set(self.company+self.product+self.category)
        self.region_tree = self.build_actree(list(self.region_words))
        self.word_type_dict = self.build_word_type_dict()

        self.category_qwds = ['类别','类','险种','产品型号']
        self.company_belong_qwds = ['什么公司','哪家的','哪个公司','销售商','公司','公司名称','售卖方']
        self.query_pro_qwds = ['产品','保险','包含','哪些','险']
        self.introduce_qwds = ['介绍','咨询','了解','科普']
        self.material_qwds = ['材料','资料','提交','准备']
        self.age_qwds = ['年龄','多大','岁']
        self.range_qwds = ['多长','周期','多少年','几年']
        self.content_qwds = ['保障','用途','有什么用','保什么','功能','保障范围']

        print('init over!')
        return

    def classify(self, question):
        data = {}
        product_dict = self.check_product(question)
        if not product_dict:
            return {}
        data['args'] = product_dict
        #收集问句当中所涉及到的实体类型
        types = []
        for type_ in product_dict.values():
            types += type_
        question_type = 'others'

        question_types = []

        #产品类别
        if self.check_words(self.category_qwds,question) and ('product' in types):
            question_type = 'product_category'
            question_types.append(question_type)
        #产品公司
        if self.check_words(self.company_belong_qwds,question) and ('product' in types):
            question_type = 'product_company'
            question_types.append(question_type)
        #某某类别有什么产品
        if self.check_words(self.query_pro_qwds,question) and ('category' in types):
            question_type = 'category_product'
            question_types.append(question_type)
        #某某公司有什么产品
        if self.check_words(self.query_pro_qwds,question) and ('company' in types):
            question_type = 'company_product'
            question_types.append(question_type)
        #产品介绍
        if self.check_words(self.introduce_qwds,question) and ('product' in types):
            question_type = 'product_introduce'
            question_types.append(question_type)
        #产品理赔材料
        if self.check_words(self.material_qwds,question) and ('product' in types):
            question_type = 'product_material'
            question_types.append(question_type)
        #产品承保年龄
        if self.check_words(self.age_qwds,question) and ('product' in types):
            question_type = 'product_age'
            question_types.append(question_type)
        #产品保障周期
        if self.check_words(self.range_qwds,question) and ('product' in types):
            question_type = 'product_range'
            question_types.append(question_type)
        #产品主要保障
        if self.check_words(self.content_qwds,question) and ('product' in types):
            question_type = 'product_content'
            question_types.append(question_type)

        data['question_type'] = question_types

        return data

    '''构造词对应的类型'''
    def build_word_type_dict(self):
        wd_dict = dict()
        for wd in self.region_words:
            wd_dict[wd] = []
            if wd in self.company:
                wd_dict[wd].append('company')
            if wd in self.product:
                wd_dict[wd].append('product')
            if wd in self.category:
                wd_dict[wd].append('category')

        return wd_dict

    '''构造actree，加速过滤'''
    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    '''问句过滤'''
    def check_product(self, question):
        region_wds = []
        for i in self.region_tree.iter(question):
            wd = i[1][1]
            region_wds.append(wd)
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)
        final_wds = [i for i in region_wds if i not in stop_wds]
        final_dict = {i:self.word_type_dict.get(i) for i in final_wds}

        return final_dict
    '''基于特征词进行分类'''
    def check_words(self, wds, sent):
        for wd in wds:
            if wd in sent:
                return True
        return False

if __name__ == '__main__':
    classifier_handler = QuestionClassifier()
    while 1:
        question = input('input an question:')
        data = classifier_handler.classify(question)
        print(data)


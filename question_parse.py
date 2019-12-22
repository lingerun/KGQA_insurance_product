#!/usr/bin/python3
# encoding: utf-8
# @author: lingyun
# @file: question_parse.py
# @time: 2018/12/18 14:48
# @desc:

from question_classifier import QuestionClassifier

class QuestionParse:

    '''构建实体节点'''
    def build_entitydict(self, args):
        entity_dict = {}
        for arg, types in args.items():
            for type in types:
                if type not in entity_dict:
                    entity_dict[type] = [arg]
                else:
                    entity_dict[type].append(arg)

        return entity_dict

    def parse_main(self, res_classify):
        args = res_classify['args']
        entity_dict = self.build_entitydict(args)
        question_types = res_classify['question_type']
        sqls = []

        for question_type in question_types:
            sql_dict = {}
            sql_dict['question_type'] = question_type
            sql = []
            if question_type == 'product_category':
                sql = self.sql_transfer(question_type, entity_dict.get('product'))
            elif question_type == 'product_company':
                sql = self.sql_transfer(question_type, entity_dict.get('product'))
            elif question_type == 'category_product':
                sql = self.sql_transfer(question_type, entity_dict.get('category'))
            elif question_type == 'company_product':
                sql = self.sql_transfer(question_type, entity_dict.get('company'))
            #查询产品属性，包括link/material/age/range/content
            else:
                sql = self.sql_transfer(question_type, entity_dict.get('product'))

            if sql:
                sql_dict['sql'] = sql
                sqls.append(sql_dict)

            return sqls

    '''针对不同的问题，分开进行处理'''
    def sql_transfer(self, question_type, entities):
        if not entities:
            return []

        # 查询语句
        sql = []
        # 查询产品种类
        if question_type == 'product_category':
            sql = ["MATCH (m:product)-[r:belong_category]->(n:category) where m.name = '{0}' \
            return m.name, r.name, n.name".format(i) for i in entities]

        #查询产品公司
        elif question_type == 'product_company':
            sql = ["MATCH (m:product)-[r:belong_company]->(n:company) where m.name = '{0}' \
            return m.name, r.name, n.name".format(i) for i in entities]

        #查询公司有哪些产品
        elif question_type == 'company_product':
            sql = ["MATCH (m:product)-[r:belong_company]->(n:company) where n.name = '{0}' \
            return m.name, r.name, n.name".format(i) for i in entities]

        #查询种类有哪些产品
        elif question_type == 'category_product':
            sql = ["MATCH (m:product)-[r:belong_category]->(n:category) where n.name = '{0}' \
            return m.name, r.name, n.name".format(i) for i in entities]
        #产品介绍/理赔材料/承保年龄/保障周期/主要保障
        else:
            sql = ["MATCH (m:product) where m.name = '{0}' return m.name, m.link, m.material, \
            m.age, m.range, m.content".format(i) for i in entities]

        #print(sql)
        return sql

if __name__ == '__main__':
    classifier_handler = QuestionClassifier()
    parse_handle = QuestionParse()
    while 1:
        question = input('input an question:')
        data = classifier_handler.classify(question)
        print(data)
        sql = parse_handle.parse_main(data)
        print(sql[0])
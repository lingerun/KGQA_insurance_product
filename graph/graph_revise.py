#!/usr/bin/python3
# encoding: utf-8
# @author: lingyun
# @file: propert_add.py
# @time: 2018/12/25 10:37
# @desc:

import pandas as pd
from py2neo import Graph,Node

class GraphRevise:
    def __init__(self):
        self.data_path = '../data/ins_product_data.xls'
        # self.g = Graph(
        #     host="localhost",
        #     http_port=7474,
        #     user="neo4j",
        #     password="neo")
        self.g = Graph("http://localhost:7474", username="ins_graph", password='ins_graph')

        data = pd.read_excel(self.data_path)

        company = data['公司名称']
        product = data['产品名称']
        category = data['类别1']
        link = data['产品链接']
        material = data['需要的理赔资料']
        age = data['承保年龄']
        range = data['保障周期']
        content = data['主要保障']

        self.product_property = list(zip(product,link,material,age,range,content))

        self.company = list(set(data['公司名称']))
        self.product = list(set(data['产品名称']))
        self.category = list(set(data['类别1']))

        self.rels_product_category = list(zip(product,category))
        self.rels_product_company = list(zip(product,company))

    def add_property(self):
        for property in self.product_property:
            query = "match(p:product) where p.name='{}' set p.link='{}',p.material='{}',p.age='{}',p.range='{}',p.content='{}'".format(property[0],property[1],property[2],property[3],property[4],property[5])
            print(query)
            self.g.run(query)

    def create_node(self):
        for cop in self.company:
            node = Node('company', name=cop)
            self.g.create(node)
        for pro in self.product:
            node = Node('product', name=pro)
            self.g.create(node)
        for cat in self.category:
            node = Node('category', name=cat)
            self.g.create(node)

        print('node create over!')

    def create_rels(self):
        self.create_relationship('product','category',self.rels_product_category,'belong_category','保险种类')
        self.create_relationship('product','company',self.rels_product_company,'belong_company','所属公司')

    '''创建实体关联边'''
    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        count = 0
        # 去重处理
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        all = len(set(set_edges))
        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            print(query)
            try:
                self.g.run(query)
                count += 1
                print(rel_type, count, all)
            except Exception as e:
                print(e)
        return


if __name__ == '__main__':
    build_handle = GraphRevise()
    build_handle.add_property()
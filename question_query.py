#!/usr/bin/python3
# encoding: utf-8
# @author: lingyun
# @file: question_query.py
# @time: 2018/12/18 14:48
# @desc:

from question_classifier import QuestionClassifier
from question_parse import QuestionParse
from py2neo import Graph

class QuestionQuery:
    def __init__(self):
        # self.g = Graph(
        #     host="localhost",
        #     http_port=7474,
        #     user="ins_graph",
        #     password="ins_graph")
        self.g = Graph("http://localhost:7474", username="ins_graph", password='ins_graph')
        self.num_limit = 20

    def query_main(self, sqls):
        final_answers = []
        for sql_dict in sqls:
            question_type = sql_dict['question_type']
            queries = sql_dict['sql']
            answers = []

            for query in queries:
                ress = self.g.run(query).data()
                answers += ress

            final_answer = self.answers_prettify(question_type, answers)
            if final_answer:
                final_answers.append(final_answer)

        return final_answers

    def answers_prettify(self,question_type,answers):
        final_answer = []
        if not answers:
            return ''
        if question_type == 'product_category':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{}属于{}'.format(subject, '、'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'product_company':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{}是{}的产品'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'category_product':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '{}有的种类：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'company_product':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '{}包含的产品：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        #产品介绍
        if question_type == 'product_introduce':
            desc = [i['m.link'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '你可以参考{}的产品链接：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        #产品理赔材料
        if question_type == 'product_material':
            desc = [i['m.material'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{}所需的理赔材料：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        #产品承保年龄
        if question_type == 'product_age':
            desc = [i['m.age'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{}的承保年龄是：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        #产品保障周期
        if question_type == 'product_range':
            desc = [i['m.range'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{}的保障范围：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        #产品主要保障
        if question_type == 'product_content':
            desc = [i['m.content'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{}主要保障是：{}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        return final_answer

if __name__ == '__main__':
    classifier_handler = QuestionClassifier()
    parse_handle = QuestionParse()
    query_handle = QuestionQuery()
    while 1:
        question = input('input an question:')
        data = classifier_handler.classify(question)
        #print(data)
        if not data:
            print(' 理解不了诶！\n','你可以这样输入：\n','  xx保险属于哪个公司\n','  人寿保险有哪些种类的保险')
        else:
            sql = parse_handle.parse_main(data)
            #print(sql[0])
            answers = query_handle.query_main(sql)
            print('\n'.join(answers))
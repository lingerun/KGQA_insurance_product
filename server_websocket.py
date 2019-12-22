#!/usr/bin/python3
# encoding: utf-8
# @author: lingyun
# @file: server_websocket.py
# @time: 2019/1/11 9:46
# @desc:

#coding=utf-8

from flask import Flask, request, render_template
from geventwebsocket.websocket import WebSocket
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
import json
from question_classifier import QuestionClassifier
from question_parse import QuestionParse
from question_query import QuestionQuery


app = Flask(__name__)

@app.route("/index/")
def index():
    return render_template("web_socket.html")


user_socket_dict = {}
@app.route("/ws/<username>")
def ws(username):
    user_socket = request.environ.get("wsgi.websocket") # type:
    if not user_socket:
        return "使用WebSocket方式连接"
    user_socket_dict[username] = user_socket
    print(user_socket_dict)
    while True:
        try:
            user_msg = user_socket.receive()

            answer(user_msg)

            for k,v in user_socket_dict.items():
                who_send_msg = {
                    "send_user": username,
                    "send_msg": user_msg,
                }

                if user_socket == v:
                    continue
                v.send(json.dumps(who_send_msg))

        except Exception as  e:
            user_socket_dict.pop(username)


def answer(question):
    classifier_handler = QuestionClassifier()
    parse_handle = QuestionParse()
    query_handle = QuestionQuery()

    data = classifier_handler.classify(question)

    if not data:
        print(' 理解不了诶！\n', '你可以这样输入：\n', '  xx保险属于哪个公司\n', '  人寿保险有哪些种类的保险')
        answers = ' 理解不了诶！你可以这样输入：xx保险属于哪个公司，人寿保险有哪些种类的保险'
    else:
        sql = parse_handle.parse_main(data)
        # print(sql[0])
        answers = query_handle.query_main(sql)
        print('\n'.join(answers))

    user_socket = request.environ.get("wsgi.websocket")
    answer_msg = {
        "send_user": 'BOT',
        "send_msg": answers,
    }

    user_socket.send(json.dumps(answer_msg))


if __name__ == '__main__':
    http_serv = WSGIServer(("0.0.0.0",5000),app,handler_class=WebSocketHandler)
    http_serv.serve_forever()

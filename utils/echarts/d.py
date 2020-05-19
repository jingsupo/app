# -*- coding: utf-8 -*-

import json
import struct
from flask import Flask, render_template, request, jsonify
import loguru as log
import pymongo
import numpy as np
import pandas as pd


# client = pymongo.MongoClient(host='192.168.2.232', port=27017)
#
# # 密码认证
# client.admin.authenticate('nego', '123456abcd.')

app = Flask(__name__, template_folder="templates")


@app.route("/")
def index():
    return render_template("d.html")


@app.route('/draw', methods=['POST'])
def draw():
    # 数据
    data1 = []
    data2 = []
    data3 = []

    # d1 = 2.4+(2.6-2.4)*np.random.rand(180)
    # d2 = 2.6+(2.8-2.6)*np.random.rand(180)
    # x = np.arange(1, 31, 1)
    # y = -(1 / 30) * x + 2.3
    # y = y + 0.5 * np.random.rand(30)
    # d3 = np.concatenate([2.5+(2.7-2.5)*np.random.rand(120), y, 1.6+(1.8-1.6)*np.random.rand(30)])
    # d1 = np.around(d1, 6)
    # d2 = np.around(d2, 6)
    # d3 = np.around(d3, 6)
    # date = pd.date_range(start='2019-10-20', periods=180, freq='d').map(lambda x: x.strftime('%Y/%m/%d'))# %H:%M:%S'))

    # x = np.arange(1, 31, 1)
    # y = -(0.2/30) * x + 0.35
    # y = y + 0.2*np.random.rand(30)
    # d1 = np.concatenate([0.4+(0.5-0.4)*np.random.rand(120), y, 0.25+(0.3-0.2)*np.random.rand(30)])
    # d2 = 0.4+(0.5-0.4)*np.random.rand(180)
    # d3 = 0.4+(0.5-0.4)*np.random.rand(180)
    # d1 = np.around(d1, 6)
    # d2 = np.around(d2, 6)
    # d3 = np.around(d3, 6)
    # date = pd.date_range(start='2019-6-20', periods=180, freq='d').map(lambda x: x.strftime('%Y/%m/%d'))# %H:%M:%S'))

    # d1 = 0.5+(0.6-0.5)*np.random.rand(180)
    # d2 = 0.5+(0.6-0.5)*np.random.rand(180)
    # d3 = 0.5+(0.6-0.5)*np.random.rand(180)
    # d1 = np.around(d1, 6)
    # d2 = np.around(d2, 6)
    # d3 = np.around(d3, 6)
    # date = pd.date_range(start='2019-6-30', periods=180, freq='d').map(lambda x: x.strftime('%Y/%m/%d'))# %H:%M:%S'))

    d1 = np.random.rand(450)
    d2 = np.random.rand(450)
    d3 = np.random.rand(450) + 0.3
    d1 = np.around(d1, 6)
    d2 = np.around(d2, 6)
    d3 = np.around(d3, 6)

    for v in zip(range(450), d1):
        dic = dict()
        dic['name'] = 'd1'
        dic['value'] = v
        data1.append(dic)

    for v in zip(range(450), d2):
        dic = dict()
        dic['name'] = 'd2'
        dic['value'] = v
        data2.append(dic)

    for v in zip(range(450), d3):
        dic = dict()
        dic['name'] = 'd3'
        dic['value'] = v
        data3.append(dic)

    dataset = dict()
    dataset['叶片1'] = data1
    dataset['叶片2'] = data2
    dataset['叶片3'] = data3

    return jsonify(dataset)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

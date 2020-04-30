# -*- coding: utf-8 -*-

import struct
from flask import Flask, render_template, request, jsonify
import loguru as log
import pymongo
import numpy as np
import pandas as pd
from scipy.fftpack import fft, ifft, hilbert


client = pymongo.MongoClient(host='192.168.2.232', port=27017)


app = Flask(__name__, template_folder="templates")


# ******频谱计算函数******
def filter_data(data, fs, low_cut, high_cut):
    d = np.array(data)
    n = len(d)
    df = fs / n
    n_low_cut = round(low_cut / df)
    n_high_cut = round(high_cut / df)
    ft = fft(d)
    ft[0:n_low_cut] = 0 + 0j
    ft[-n_low_cut:n] = 0 + 0j
    ft[n_high_cut:-n_high_cut] = 0 + 0j
    filtered_data = ifft(ft).real
    return filtered_data


def fourier_transform(data, fs):
    d = np.array(data)
    n = len(d)
    df = fs / n
    ft = fft(d)
    ft = abs(ft) * 2 / n
    am = ft[0:int(np.round(n / 2))]
    fre = np.arange(int(np.round(n / 2))) * df
    return fre, am


def envelop(data, fs, low_cutoff, high_cutoff):
    filtered_data = filter_data(data, fs, low_cutoff, high_cutoff)
    hx = hilbert(filtered_data)
    x = np.sqrt(filtered_data ** 2 + hx ** 2)
    x = x - np.mean(x)
    fre, am = fourier_transform(x, fs)
    return fre, am, x
# ******频谱计算函数******


@app.route("/")
def index():
    return render_template("demo.html")


@app.route('/get_db_names', methods=['POST'])
def get_db_names():
    db_names = client.list_database_names()[:-3]

    return jsonify(db_names)


@app.route('/farm', methods=['POST'])
def farm():
    dbname = request.form.get('farm_name')
    db = client[dbname]
    collection = db.list_collection_names()

    return jsonify(collection)


@app.route('/q', methods=['POST'])
def q():
    dbname = request.form.get('farm_name')
    db = client[dbname]
    collection = request.form.get('wind_turbine_name')
    time = request.form.get('sampling_time')

    # 所选时间范围内的采样时间
    sampling_time_dict = db[collection].find({'sampling_time': {'$regex': time}}, {'_id': 0, 'sampling_time': 1})
    sampling_time_str = [val for dic in sampling_time_dict for key, val in dic.items()]

    # 测点信息
    point_description = db['information'].find_one({'desc': '机组信息'})['point_description']

    # 转速
    rotate_speed = db['information'].find_one({'desc': '机组信息'})['rotate_speed'][collection]

    return jsonify({'sampling_time': sampling_time_str,
                    'point_description': point_description,
                    'rotate_speed': rotate_speed})


@app.route('/toolbar1', methods=['POST'])
def toolbar1():
    dbname = request.form.get('farm_name')
    db = client[dbname]
    collection = request.form.get('wind_turbine_name')
    sampling_time = request.form.get('sampling_time')
    # 当前选中测点的中文描述
    point_zh = request.form.get('point')

    # 测点信息
    point_description = db['information'].find_one({'desc': '机组信息'})['point_description']
    # 当前选中测点的中文描述对应的数据库中的键
    point = [key for key in point_description if point_description[key] == point_zh][0]

    data = db[collection].find_one({'sampling_time': sampling_time})

    dataset = dict()

    # 时域数据
    time_series = []
    # 频域数据
    freq = []

    try:
        if 'drivechain_' in point:
            data_length = str(data['data_length_drivechain'])
            # sampling_fre = data['sampling_fre_drivechain']
        elif 'tower_' in point:
            data_length = str(data['data_length_tower'])
            # sampling_fre = data['sampling_fre_tower']

        data = struct.unpack(data_length + 'f', data[point])

        for v in zip(range(len(data)), data):
            dic = dict()
            dic['name'] = 'ts'
            dic['value'] = v
            time_series.append(dic)

        # FFT
        n = len(data)
        ft = abs(fft(data)) * 2 / n
        freq_amp = ft[range(int(n / 2))]

        for v in zip(range(len(freq_amp)), freq_amp):
            dic = dict()
            dic['name'] = 'freq'
            dic['value'] = v
            freq.append(dic)

    except KeyError:
        log.logger.debug('无此测点数据')

    dataset['time_series'] = time_series
    dataset['freq'] = freq

    return jsonify(dataset)


@app.route('/toolbar2', methods=['POST'])
def toolbar2():
    dataset = {'info': 'good'}

    return jsonify(dataset)


if __name__ == "__main__":
    app.run(debug=True)

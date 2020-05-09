# -*- coding: utf-8 -*-

import json
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
    collection = [c for c in db.list_collection_names() if c not in ['information', 'eigen_value']]
    collection.sort()

    return jsonify(collection)


@app.route('/q', methods=['POST'])
def q():
    dbname = request.form.get('farm_name')
    db = client[dbname]
    collection = request.form.get('wind_turbine_name')
    from_time = request.form.get('from_time')
    to_time = request.form.get('to_time')
    from_rotate_speed = request.form.get('from_rotate_speed')
    to_rotate_speed = request.form.get('to_rotate_speed')

    # 测点信息
    point_description = db['information'].find_one({'desc': '机组信息'})['point_description']

    # 转速
    rotate_speed = db['information'].find_one({'desc': '机组信息'})['rotate_speed'][collection]

    rs = pd.DataFrame(rotate_speed.items())

    if from_time != '' and to_time != '' and from_rotate_speed != '选择转速' and to_rotate_speed != '选择转速':
        from_rotate_speed = float(from_rotate_speed)
        to_rotate_speed = float(to_rotate_speed)
        rs = rs[(rs.iloc[:, 0] >= from_time) & (rs.iloc[:, 0] <= to_time)]
        rs = rs[(rs.iloc[:, 1] >= from_rotate_speed) & (rs.iloc[:, 1] <= to_rotate_speed)]

    sampling_time = rs.iloc[:, 0].tolist()

    return jsonify({'sampling_time': sampling_time,
                    'point_description': point_description,
                    'rotate_speed': rotate_speed})


@app.route('/tf', methods=['POST'])
def tf():
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

    # 时域数据
    time_series = []
    # 频域数据
    freq = []

    try:
        if 'drivechain_' in point:
            if 'data_length_drivechain' in data.keys():
                data_length = str(data['data_length_drivechain'])
                sampling_fre = data['sampling_fre_drivechain']
            elif int(point[-1]) < 6:
                data_length = str(data['data_length_drivechain_15'])
                sampling_fre = data['sampling_fre_drivechain_15']
            else:
                data_length = str(data['data_length_drivechain_68'])
                sampling_fre = data['sampling_fre_drivechain_68']
        elif 'tower_' in point:
            data_length = str(data['data_length_tower'])
            sampling_fre = data['sampling_fre_tower']
        elif 'nacelle_' in point:
            data_length = str(data['data_length_nacelle'])
            sampling_fre = data['sampling_fre_nacelle']
        else:
            if int(point[-1]) < 6:
                data_length = str(data['data_nums_15'][0])
                sampling_fre = data['sampling_fre_15']
            else:
                data_length = str(data['data_nums_68'][0])
                sampling_fre = data['sampling_fre_68']

        data = struct.unpack(data_length + 'f', data[point])

        for v in zip(range(len(data)), data):
            dic = dict()
            dic['name'] = 'ts'
            dic['value'] = v
            time_series.append(dic)

        fre, am = fourier_transform(data, sampling_fre)

        for v in zip(fre, am):
            dic = dict()
            dic['name'] = 'freq'
            dic['value'] = v
            freq.append(dic)

    except Exception as e:
        log.logger.debug(e)

    dataset = dict()
    dataset['time_series'] = time_series
    dataset['freq'] = freq

    return jsonify(dataset)


@app.route('/envelope', methods=['POST'])
def envelope():
    dbname = request.form.get('farm_name')
    db = client[dbname]
    collection = request.form.get('wind_turbine_name')
    sampling_time = request.form.get('sampling_time')
    # 当前选中测点的中文描述
    point_zh = request.form.get('point')
    low_cutoff = float(request.form.get('low_cutoff'))
    high_cutoff = float(request.form.get('high_cutoff'))

    # 测点信息
    point_description = db['information'].find_one({'desc': '机组信息'})['point_description']
    # 当前选中测点的中文描述对应的数据库中的键
    point = [key for key in point_description if point_description[key] == point_zh][0]

    data = db[collection].find_one({'sampling_time': sampling_time})

    # 频谱包络数据
    spectrum_envelope = []

    try:
        if 'drivechain_' in point:
            if 'data_length_drivechain' in data.keys():
                data_length = str(data['data_length_drivechain'])
                sampling_fre = data['sampling_fre_drivechain']
            elif int(point[-1]) < 6:
                data_length = str(data['data_length_drivechain_15'])
                sampling_fre = data['sampling_fre_drivechain_15']
            else:
                data_length = str(data['data_length_drivechain_68'])
                sampling_fre = data['sampling_fre_drivechain_68']
        elif 'tower_' in point:
            data_length = str(data['data_length_tower'])
            sampling_fre = data['sampling_fre_tower']
        elif 'nacelle_' in point:
            data_length = str(data['data_length_nacelle'])
            sampling_fre = data['sampling_fre_nacelle']
        else:
            if int(point[-1]) < 6:
                data_length = str(data['data_nums_15'][0])
                sampling_fre = data['sampling_fre_15']
            else:
                data_length = str(data['data_nums_68'][0])
                sampling_fre = data['sampling_fre_68']

        data = struct.unpack(data_length + 'f', data[point])

        # spectrum envelope
        fre, am, _ = envelop(data, sampling_fre, low_cutoff, high_cutoff)

        for v in zip(fre, am):
            dic = dict()
            dic['name'] = 'envelope'
            dic['value'] = v
            spectrum_envelope.append(dic)

    except Exception as e:
        log.logger.debug(e)

    dataset = dict()
    dataset['envelope'] = spectrum_envelope[:500]

    return jsonify(dataset)


@app.route('/trend', methods=['POST'])
def trend():
    dbname = request.form.get('farm_name')
    db = client[dbname]
    from_time = request.form.get('from_time')
    to_time = request.form.get('to_time')
    from_rotate_speed = request.form.get('from_rotate_speed')
    to_rotate_speed = request.form.get('to_rotate_speed')
    from_rotate_speed = float(from_rotate_speed)
    to_rotate_speed = float(to_rotate_speed)
    # 当前选中测点的中文描述
    point_zh = request.form.get('point')
    criterion = request.form.get('criterion')
    collection = request.form.get('wind_turbine_selected')
    collection = json.loads(collection)

    # 测点信息
    point_description = db['information'].find_one({'desc': '机组信息'})['point_description']
    # 当前选中测点的中文描述对应的数据库中的键
    point = [key for key in point_description if point_description[key] == point_zh][0]

    # VDI数据
    vdi = {}
    # 无量纲数据
    dimensionless = {}

    data = {}
    for c in collection:
        if criterion == '1':
            data[c] = db['eigen_value'].find_one({'criterion': 'VDI3834', 'windturbine': c})
        else:
            data[c] = db['eigen_value'].find_one({'criterion': 'dimensionless', 'windturbine': c})

    if criterion == '1':
        for c in collection:
            print(c)
            df = pd.DataFrame([data[c]['date_time'], data[c]['rotate_speed']]).T
            if df.iloc[:, 1].dtype is not float:
                df.iloc[:, 1] = df.iloc[:, 1].astype('float')
            df = df[(df.iloc[:, 0] >= from_time) & (df.iloc[:, 0] <= to_time)]
            df = df[(df.iloc[:, 1] >= from_rotate_speed) & (df.iloc[:, 1] <= to_rotate_speed)]

            if point[-1] == '1':
                ev = data[c]['EV_VDI_1']
                iv = data[c]['IV_VDI_1']
            elif point[-1] == '2':
                ev = data[c]['EV_VDI_2']
                iv = data[c]['IV_VDI_2']
            else:
                ev = []
                iv = []

            ev = np.array(ev)[df.index]
            iv = np.array(iv)[df.index]
            ret = pd.concat([df.reset_index(drop=True), pd.Series(ev)], axis=1)
            ret = pd.concat([ret, pd.Series(iv)], axis=1)
            ret.columns = ['time', 'rotate_speed', 'ev', 'iv']
            ret['ev'] = ret['ev'].round(decimals=6)
            ret['iv'] = ret['iv'].round(decimals=6)

            vdi[c] = {}
            vdi[c]['ev'] = []
            vdi[c]['iv'] = []
            vdi[c]['time'] = ret['time'].tolist()
            for v in zip(range(len(ret['ev'].tolist())), ret['ev'].tolist()):
                dic = dict()
                dic['name'] = 'ev'
                dic['value'] = v
                vdi[c]['ev'].append(dic)
            for v in zip(range(len(ret['iv'].tolist())), ret['iv'].tolist()):
                dic = dict()
                dic['name'] = 'iv'
                dic['value'] = v
                vdi[c]['iv'].append(dic)

    dataset = dict()
    dataset['vdi'] = vdi
    dataset['dimensionless'] = dimensionless

    return jsonify(dataset)


if __name__ == "__main__":
    app.run(debug=True)

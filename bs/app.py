# -*- coding: utf-8 -*-

import json
import struct
from flask import Flask, render_template, request, jsonify
import loguru as log
import numpy as np
import pandas as pd
import pymongo
from scipy.fftpack import fft, ifft, hilbert


# client = pymongo.MongoClient()
client = pymongo.MongoClient(host='192.168.2.232', port=27017)

# 密码认证
client.admin.authenticate('nego', '123456abcd.')

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


@app.route("/2", methods=['POST', 'GET'])
def index2():
    if request.method == 'POST':
        st = request.form
        return render_template("demo2.html", st=st)


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


@app.route('/tfe', methods=['POST'])
def tfe():
    dbname = request.form.get('farm_name')
    db = client[dbname]
    collection = request.form.get('wind_turbine_name')
    sampling_time = request.form.get('sampling_time')
    # 当前选中测点的中文描述
    point_zh = request.form.get('point')
    low_cutoff = request.form.get('low_cutoff')
    high_cutoff = request.form.get('high_cutoff')
    if low_cutoff != '' and high_cutoff != '':
        low_cutoff = float(low_cutoff)
        high_cutoff = float(high_cutoff)

    # 测点信息
    point_description = db['information'].find_one({'desc': '机组信息'})['point_description']
    # 当前选中测点的中文描述对应的数据库中的键
    point = [key for key in point_description if point_description[key] == point_zh][0]

    data = db[collection].find_one({'sampling_time': sampling_time})

    # 时域数据
    time_series = []
    # 频域数据
    freq = []
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
        elif 'blade_' in point:
            data_length = str(data['data_length_blade'])
            sampling_fre = data['sampling_fre_blade']
        else:
            if int(point[-1]) < 6:
                data_length = str(data['data_nums_15'][0])
                sampling_fre = data['sampling_fre_15']
            else:
                data_length = str(data['data_nums_68'][0])
                sampling_fre = data['sampling_fre_68']

        data = struct.unpack(data_length + 'f', data[point])
        data = pd.Series(data)
        data = data.round(decimals=6)

        # time series
        for v in zip(range(len(data)), data):
            dic = dict()
            dic['name'] = 'ts'
            dic['value'] = v
            time_series.append(dic)

        # freq
        fre, am = fourier_transform(data, sampling_fre)
        am = pd.Series(am)
        am = am.round(decimals=6)

        for v in zip(fre, am):
            dic = dict()
            dic['name'] = 'freq'
            dic['value'] = v
            freq.append(dic)

        if low_cutoff != '' and high_cutoff != '':
            # spectrum envelope
            fre, am, _ = envelop(data, sampling_fre, low_cutoff, high_cutoff)
            am = pd.Series(am)
            am = am.round(decimals=6)

            for v in zip(fre, am):
                dic = dict()
                dic['name'] = 'envelope'
                dic['value'] = v
                spectrum_envelope.append(dic)

    except Exception as e:
        log.logger.debug(e)

    dataset = dict()
    dataset['time_series'] = time_series
    dataset['freq'] = freq
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
            df = pd.DataFrame([data[c]['date_time'], data[c]['rotate_speed']]).T
            if df.iloc[:, 1].dtype is not float:
                df.iloc[:, 1] = df.iloc[:, 1].astype('float')
            df = df[(df.iloc[:, 0] >= from_time) & (df.iloc[:, 0] <= to_time)]
            df = df[(df.iloc[:, 1] >= from_rotate_speed) & (df.iloc[:, 1] <= to_rotate_speed)]

            ev = []
            ev2 = []
            iv = []

            if point[-1] == '1':
                ev = data[c]['EV_VDI_1']
                iv = data[c]['IV_VDI_1']
            elif point[-1] == '2':
                ev = data[c]['EV_VDI_2']
                iv = data[c]['IV_VDI_2']
            elif point[-1] == '3':
                ev = data[c]['EV_VDI_3']
                ev2 = data[c]['EV2_VDI_3']
                iv = data[c]['IV_VDI_3']
            elif point[-1] == '4':
                ev = data[c]['EV_VDI_4']
                ev2 = data[c]['EV2_VDI_4']
                iv = data[c]['IV_VDI_4']
            elif point[-1] == '5':
                ev = data[c]['EV_VDI_5']
                ev2 = data[c]['EV2_VDI_5']
                iv = data[c]['IV_VDI_5']
            elif point[-1] == '6':
                ev = data[c]['EV_VDI_6']
                ev2 = data[c]['EV2_VDI_6']
                iv = data[c]['IV_VDI_6']
            elif point[-1] == '7':
                ev = data[c]['EV_VDI_7']
                iv = data[c]['IV_VDI_7']
            elif point[-1] == '8':
                ev = data[c]['EV_VDI_8']
                iv = data[c]['IV_VDI_8']

            ev = np.array(ev)[df.index]
            iv = np.array(iv)[df.index]
            new_df = df.reset_index(drop=True).rename(columns={0: 'time', 1: 'rotate_speed'})
            ret = pd.concat([new_df, pd.Series(ev).rename('ev')], axis=1)
            ret = pd.concat([ret, pd.Series(iv).rename('iv')], axis=1)
            ret['ev'] = ret['ev'].round(decimals=6)
            ret['iv'] = ret['iv'].round(decimals=6)
            if ev2:
                ev2 = np.array(ev2)[df.index]
                ret = pd.concat([ret, pd.Series(ev2).rename('ev2')], axis=1)
                ret['ev2'] = ret['ev2'].round(decimals=6)
            ret['date'] = pd.to_datetime(ret['time']).map(lambda x: x.strftime('%Y/%m/%d %H:%M:%S'))

            vdi[c] = {}
            vdi[c]['ev'] = []
            vdi[c]['ev2'] = []
            vdi[c]['iv'] = []
            vdi[c]['time'] = ret['time'].tolist()
            for v in zip(ret['date'], ret['ev']):
                dic = dict()
                dic['name'] = 'ev'
                dic['value'] = v
                vdi[c]['ev'].append(dic)
            for v in zip(ret['date'], ret['iv']):
                dic = dict()
                dic['name'] = 'iv'
                dic['value'] = v
                vdi[c]['iv'].append(dic)
            if 'ev2' in ret.columns:
                for v in zip(ret['date'], ret['ev2']):
                    dic = dict()
                    dic['name'] = 'ev2'
                    dic['value'] = v
                    vdi[c]['ev2'].append(dic)
    else:
        for c in collection:
            df = pd.DataFrame([data[c]['date_time'], data[c]['rotate_speed']]).T
            if df.iloc[:, 1].dtype is not float:
                df.iloc[:, 1] = df.iloc[:, 1].astype('float')
            df = df[(df.iloc[:, 0] >= from_time) & (df.iloc[:, 0] <= to_time)]
            df = df[(df.iloc[:, 1] >= from_rotate_speed) & (df.iloc[:, 1] <= to_rotate_speed)]

            kurtosisfactor = []
            kurtosisfactor2 = []
            pulsefactor = []
            pulsefactor2 = []

            if point[-1] == '1':
                kurtosisfactor = data[c]['kurtosisfactor_1']
                pulsefactor = data[c]['pulsefactor_1']
            elif point[-1] == '2':
                kurtosisfactor = data[c]['kurtosisfactor_2']
                pulsefactor = data[c]['pulsefactor_2']
            elif point[-1] == '3':
                kurtosisfactor = data[c]['kurtosisfactor_3']
                kurtosisfactor2 = data[c]['kurtosisfactor2_3']
                pulsefactor = data[c]['pulsefactor_3']
                pulsefactor2 = data[c]['pulsefactor2_3']
            elif point[-1] == '4':
                kurtosisfactor = data[c]['kurtosisfactor_4']
                kurtosisfactor2 = data[c]['kurtosisfactor2_4']
                pulsefactor = data[c]['pulsefactor_4']
                pulsefactor2 = data[c]['pulsefactor2_4']
            elif point[-1] == '5':
                kurtosisfactor = data[c]['kurtosisfactor_5']
                kurtosisfactor2 = data[c]['kurtosisfactor2_5']
                pulsefactor = data[c]['pulsefactor_5']
                pulsefactor2 = data[c]['pulsefactor2_5']
            elif point[-1] == '6':
                kurtosisfactor = data[c]['kurtosisfactor_6']
                kurtosisfactor2 = data[c]['kurtosisfactor2_6']
                pulsefactor = data[c]['pulsefactor_6']
                pulsefactor2 = data[c]['pulsefactor2_6']
            elif point[-1] == '7':
                kurtosisfactor = data[c]['kurtosisfactor_7']
                pulsefactor = data[c]['pulsefactor_7']
            elif point[-1] == '8':
                kurtosisfactor = data[c]['kurtosisfactor_8']
                pulsefactor = data[c]['pulsefactor_8']

            kurtosisfactor = np.array(kurtosisfactor)[df.index]
            pulsefactor = np.array(pulsefactor)[df.index]
            new_df = df.reset_index(drop=True).rename(columns={0: 'time', 1: 'rotate_speed'})
            ret = pd.concat([new_df, pd.Series(kurtosisfactor).rename('kurtosisfactor')], axis=1)
            ret = pd.concat([ret, pd.Series(pulsefactor).rename('pulsefactor')], axis=1)
            ret['kurtosisfactor'] = ret['kurtosisfactor'].round(decimals=6)
            ret['pulsefactor'] = ret['pulsefactor'].round(decimals=6)
            if kurtosisfactor2:
                kurtosisfactor2 = np.array(kurtosisfactor2)[df.index]
                ret = pd.concat([ret, pd.Series(kurtosisfactor2).rename('kurtosisfactor2')], axis=1)
                ret['kurtosisfactor2'] = ret['kurtosisfactor2'].round(decimals=6)
            if pulsefactor2:
                pulsefactor2 = np.array(pulsefactor2)[df.index]
                ret = pd.concat([ret, pd.Series(pulsefactor2).rename('pulsefactor2')], axis=1)
                ret['pulsefactor2'] = ret['pulsefactor2'].round(decimals=6)
            ret['date'] = pd.to_datetime(ret['time']).map(lambda x: x.strftime('%Y/%m/%d %H:%M:%S'))

            dimensionless[c] = {}
            dimensionless[c]['kurtosisfactor'] = []
            dimensionless[c]['kurtosisfactor2'] = []
            dimensionless[c]['pulsefactor'] = []
            dimensionless[c]['pulsefactor2'] = []
            dimensionless[c]['time'] = ret['time'].tolist()
            for v in zip(ret['date'], ret['kurtosisfactor']):
                dic = dict()
                dic['name'] = 'kurtosisfactor'
                dic['value'] = v
                dimensionless[c]['kurtosisfactor'].append(dic)
            for v in zip(ret['date'], ret['pulsefactor']):
                dic = dict()
                dic['name'] = 'pulsefactor'
                dic['value'] = v
                dimensionless[c]['pulsefactor'].append(dic)
            if 'kurtosisfactor2' in ret.columns:
                for v in zip(ret['date'], ret['kurtosisfactor2']):
                    dic = dict()
                    dic['name'] = 'kurtosisfactor2'
                    dic['value'] = v
                    dimensionless[c]['kurtosisfactor2'].append(dic)
            if 'pulsefactor2' in ret.columns:
                for v in zip(ret['date'], ret['pulsefactor2']):
                    dic = dict()
                    dic['name'] = 'pulsefactor2'
                    dic['value'] = v
                    dimensionless[c]['pulsefactor2'].append(dic)

    dataset = dict()
    dataset['vdi'] = vdi
    dataset['dimensionless'] = dimensionless

    return jsonify(dataset)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

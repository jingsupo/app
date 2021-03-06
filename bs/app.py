# -*- coding: utf-8 -*-

import base64
import datetime
import hashlib
import json
import os
import struct
from flask import Flask, render_template, request, jsonify
import loguru as log
import numpy as np
import pandas as pd
import pymongo
from scipy.fftpack import fft, ifft, hilbert


local = pymongo.MongoClient()
client = pymongo.MongoClient(host='192.168.2.232', port=27017)

# 密码认证
client.admin.authenticate('nego', '123456abcd.')

app = Flask(__name__, static_url_path='', static_folder='')
# # 默认缓存控制的最大期限，以秒计
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = datetime.timedelta(seconds=1)


@app.route('/getpass', methods=['POST'])
def getpass():
    _pass = client['management']['pass'].find_one()['password']

    return jsonify({'pass': _pass})


# 获取目录下所有图片的md5值
def get_picture_md5(path):
    filename = os.listdir(path)
    filepath = [os.path.join(path, fn) for fn in filename if fn.lower().endswith(('jpg', 'jpeg', 'png'))]

    md5 = {}
    for i, fp in enumerate(filepath):
        with open(fp, 'rb') as f:
            md5.update({hashlib.md5(f.read()).hexdigest(): filename[i]})

    return md5


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
    return render_template("index.html")


@app.route("/draw")
def draw():
    return render_template("draw.html")


@app.route("/demo")
def demo():
    return render_template("demo.html")


@app.route('/get_db_names', methods=['POST'])
def get_db_names():
    to_remove = ['admin', 'config', 'local', 'management']
    db_names = [db for db in client.list_database_names() if db not in to_remove]

    return jsonify(db_names)


@app.route('/farm', methods=['POST'])
def farm():
    dbname = request.form.get('farm_name')
    db = client[dbname]
    collection = [c for c in db.list_collection_names() if c not in ['information', 'eigenvalue']]
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
    # 对字典根据键值分组进行排序
    point_description = sorted(point_description.items(), key=lambda x: (x[0].split('_')[0], int(x[0].split('_')[1])))
    point_description = [x[1] for x in point_description]

    # 转速
    rotate_speed = db['information'].find_one({'desc': '机组信息'})['rotate_speed'][collection]

    rs = pd.DataFrame(rotate_speed.items())

    if from_time != '' and to_time != '' and from_rotate_speed != '' and to_rotate_speed != '':
        from_rotate_speed = float(from_rotate_speed)
        to_rotate_speed = float(to_rotate_speed)
        rs = rs[(rs.iloc[:, 0] >= from_time) & (rs.iloc[:, 0] <= to_time)]
        rs = rs[(rs.iloc[:, 1] >= from_rotate_speed) & (rs.iloc[:, 1] <= to_rotate_speed)]

    sampling_time = (rs.iloc[:, 0] + ':转速 ' + rs.iloc[:, 1].astype('str')).tolist()
    sampling_time = sorted(sampling_time, key=lambda x: x.split(':')[0], reverse=True)

    return jsonify({'sampling_time': sampling_time,
                    'point_description': point_description})


@app.route('/tfe', methods=['POST'])
def tfe():
    dbname = request.form.get('farm_name')
    db = client[dbname]
    collection = request.form.get('wind_turbine_name')
    sampling_time = request.form.get('sampling_time')
    # 当前选中测点的中文描述
    point_zh = request.form.get('point')
    # 获取时域频域包络复选框的选中状态
    ts_checked = request.form.get('ts_checked')
    freq_checked = request.form.get('freq_checked')
    env_checked = request.form.get('env_checked')
    if ts_checked == 'true':
        ts_checked = True
    else:
        ts_checked = False
    if freq_checked == 'true':
        freq_checked = True
    else:
        freq_checked = False
    if env_checked == 'true':
        env_checked = True
    else:
        env_checked = False
    # 要请求的图形类型(时域频域、包络)
    fig_type = request.form.get('fig_type')
    if env_checked or fig_type == '2':
        low_cutoff = request.form.get('low_cutoff')
        high_cutoff = request.form.get('high_cutoff')
        if low_cutoff != '' and high_cutoff != '':
            low_cutoff = float(low_cutoff)
            high_cutoff = float(high_cutoff)
    else:
        low_cutoff = ''
        high_cutoff = ''

    # 测点信息
    point_description = db['information'].find_one({'desc': '机组信息'})['point_description']
    # 当前选中测点的中文描述对应的数据库中的键
    point = [key for key in point_description if point_description[key] == point_zh][0]
    point_num = point.split('_')[-1]

    data = db[collection].find_one({'sampling_time': sampling_time})

    # 采样频率
    sampling_fre = 0

    # 时域数据
    time_series = []
    # 频域数据
    freq = []
    # 频谱包络数据
    spectrum_envelope = []

    try:
        if 'drivechain_' in point:
            if 'data_length_drivechain' in data.keys():
                data_length = data['data_length_drivechain']
                sampling_fre = data['sampling_fre_drivechain']
            elif int(point_num) < 6:
                data_length = data['data_length_drivechain_15']
                sampling_fre = data['sampling_fre_drivechain_15']
            else:
                data_length = data['data_length_drivechain_68']
                sampling_fre = data['sampling_fre_drivechain_68']
        elif 'tower_' in point:
            data_length = data['data_length_tower']
            sampling_fre = data['sampling_fre_tower']
        elif 'nacelle_' in point:
            data_length = data['data_length_nacelle']
            sampling_fre = data['sampling_fre_nacelle']
        elif 'blade_' in point:
            data_length = data['data_length_blade']
            sampling_fre = data['sampling_fre_blade']
        else:
            if int(point_num) < 6:
                data_length = data['data_nums_15'][0]
                sampling_fre = data['sampling_fre_15']
            else:
                data_length = data['data_nums_68'][0]
                sampling_fre = data['sampling_fre_68']

        data = struct.unpack(str(data_length) + 'f', data[point])
        data = pd.Series(data)
        data = data.round(decimals=6)

        if ts_checked or fig_type == '1':
            # time series
            # for v in zip(range(len(data)), data):
            #     time_series.append(v)

            time_series = data.tolist()

        if freq_checked or fig_type == '1':
            # freq
            fre, am = fourier_transform(data, sampling_fre)
            am = pd.Series(am)
            am = am.round(decimals=6)

            for v in zip(fre, am):
                freq.append(v)

        if env_checked or fig_type == '2':
            # spectrum envelope
            if low_cutoff != '' and high_cutoff != '':
                fre, am, _ = envelop(data, sampling_fre, low_cutoff, high_cutoff)
                am = pd.Series(am)
                am = am.round(decimals=6)

                for v in zip(fre, am):
                    spectrum_envelope.append(v)

    except Exception as e:
        log.logger.debug(e)

    dataset = dict()
    dataset['fs'] = sampling_fre
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
    point_num = point.split('_')[-1]

    # VDI数据
    vdi = {}
    # 无量纲数据
    dimensionless = {}
    # narrowband数据
    narrowband = {}

    data = {}
    for c in collection:
        if criterion == '1':
            data[c] = db['eigenvalue'].find_one({'criterion': 'VDI3834', 'windturbine': c})
        if criterion == '2':
            data[c] = db['eigenvalue'].find_one({'criterion': 'dimensionless', 'windturbine': c})
        if criterion == '3':
            data[c] = db['eigenvalue'].find_one({'criterion': 'narrowband', 'windturbine': c})

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
            ret = pd.DataFrame()

            if 'drivechain_' in point or 'vibration_' in point:
                if point_num == '1':
                    ev = data[c]['EV_VDI_1']
                    iv = data[c]['IV_VDI_1']
                elif point_num == '2':
                    ev = data[c]['EV_VDI_2']
                    if 'EV2_VDI_2' in data[c].keys():
                        ev2 = data[c]['EV2_VDI_2']
                    iv = data[c]['IV_VDI_2']
                elif point_num == '3':
                    ev = data[c]['EV_VDI_3']
                    ev2 = data[c]['EV2_VDI_3']
                    iv = data[c]['IV_VDI_3']
                elif point_num == '4':
                    ev = data[c]['EV_VDI_4']
                    ev2 = data[c]['EV2_VDI_4']
                    iv = data[c]['IV_VDI_4']
                elif point_num == '5':
                    ev = data[c]['EV_VDI_5']
                    if 'EV2_VDI_5' in data[c].keys():
                        ev2 = data[c]['EV2_VDI_5']
                    iv = data[c]['IV_VDI_5']
                elif point_num == '6':
                    ev = data[c]['EV_VDI_6']
                    if 'EV2_VDI_6' in data[c].keys():
                        ev2 = data[c]['EV2_VDI_6']
                    iv = data[c]['IV_VDI_6']
                elif point_num == '7':
                    ev = data[c]['EV_VDI_7']
                    if 'EV2_VDI_7' in data[c].keys():
                        ev2 = data[c]['EV2_VDI_7']
                    iv = data[c]['IV_VDI_7']
                elif point_num == '8':
                    ev = data[c]['EV_VDI_8']
                    if 'EV2_VDI_8' in data[c].keys():
                        ev2 = data[c]['EV2_VDI_8']
                    iv = data[c]['IV_VDI_8']
                elif point_num == '9':
                    ev = data[c]['EV_VDI_9']
                    iv = data[c]['IV_VDI_9']
                elif point_num == '10':
                    ev = data[c]['EV_VDI_10']
                    iv = data[c]['IV_VDI_10']
                elif point_num == '11':
                    ev = data[c]['EV_VDI_11']
                    iv = data[c]['IV_VDI_11']

            if ev and iv:
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
            if not ret.empty:
                ret['date'] = pd.to_datetime(ret['time']).map(lambda x: x.strftime('%Y/%m/%d %H:%M:%S'))
                # 个别机组特征值中存在NaN，需要删除，否则数据传不回前端
                ret = ret.dropna()
                ret = ret.sort_values(by='date')
                ret.reset_index(drop=True, inplace=True)

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
    if criterion == '2':
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

            if point_num == '1':
                kurtosisfactor = data[c]['kurtosisfactor_1']
                pulsefactor = data[c]['pulsefactor_1']
            elif point_num == '2':
                kurtosisfactor = data[c]['kurtosisfactor_2']
                pulsefactor = data[c]['pulsefactor_2']
            elif point_num == '3':
                kurtosisfactor = data[c]['kurtosisfactor_3']
                kurtosisfactor2 = data[c]['kurtosisfactor2_3']
                pulsefactor = data[c]['pulsefactor_3']
                pulsefactor2 = data[c]['pulsefactor2_3']
            elif point_num == '4':
                kurtosisfactor = data[c]['kurtosisfactor_4']
                kurtosisfactor2 = data[c]['kurtosisfactor2_4']
                pulsefactor = data[c]['pulsefactor_4']
                pulsefactor2 = data[c]['pulsefactor2_4']
            elif point_num == '5':
                kurtosisfactor = data[c]['kurtosisfactor_5']
                kurtosisfactor2 = data[c]['kurtosisfactor2_5']
                pulsefactor = data[c]['pulsefactor_5']
                pulsefactor2 = data[c]['pulsefactor2_5']
            elif point_num == '6':
                kurtosisfactor = data[c]['kurtosisfactor_6']
                kurtosisfactor2 = data[c]['kurtosisfactor2_6']
                pulsefactor = data[c]['pulsefactor_6']
                pulsefactor2 = data[c]['pulsefactor2_6']
            elif point_num == '7':
                kurtosisfactor = data[c]['kurtosisfactor_7']
                pulsefactor = data[c]['pulsefactor_7']
            elif point_num == '8':
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
            ret = ret.sort_values(by='date')
            ret.reset_index(drop=True, inplace=True)

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
    if criterion == '3':
        for c in collection:
            df = pd.DataFrame([data[c]['data_time'], data[c]['rotation_speed']]).T
            if df.iloc[:, 1].dtype is not float:
                df.iloc[:, 1] = df.iloc[:, 1].astype('float')
            df = df[(df.iloc[:, 0] >= from_time) & (df.iloc[:, 0] <= to_time)]
            df = df[(df.iloc[:, 1] >= from_rotate_speed) & (df.iloc[:, 1] <= to_rotate_speed)]

            value_rms = []
            value_kurtosis = []

            if point_num == '3':
                value_rms = data[c]['value_rms_3']
                value_kurtosis = data[c]['value_kurtosis_3']
            elif point_num == '4':
                value_rms = data[c]['value_rms_4']
                value_kurtosis = data[c]['value_kurtosis_4']

            value_rms = np.array(value_rms)[df.index]
            value_kurtosis = np.array(value_kurtosis)[df.index]
            new_df = df.reset_index(drop=True).rename(columns={0: 'time', 1: 'rotate_speed'})
            ret = pd.concat([new_df, pd.Series(value_rms).rename('value_rms')], axis=1)
            ret = pd.concat([ret, pd.Series(value_kurtosis).rename('value_kurtosis')], axis=1)
            ret['value_rms'] = ret['value_rms'].round(decimals=6)
            ret['value_kurtosis'] = ret['value_kurtosis'].round(decimals=6)
            ret['date'] = pd.to_datetime(ret['time']).map(lambda x: x.strftime('%Y/%m/%d %H:%M:%S'))
            ret = ret.sort_values(by='date')
            ret.reset_index(drop=True, inplace=True)

            narrowband[c] = {}
            narrowband[c]['value_rms'] = []
            narrowband[c]['value_kurtosis'] = []
            narrowband[c]['time'] = ret['time'].tolist()
            for v in zip(ret['date'], ret['value_rms']):
                dic = dict()
                dic['name'] = 'value_rms'
                dic['value'] = v
                narrowband[c]['value_rms'].append(dic)
            for v in zip(ret['date'], ret['value_kurtosis']):
                dic = dict()
                dic['name'] = 'value_kurtosis'
                dic['value'] = v
                narrowband[c]['value_kurtosis'].append(dic)

    dataset = dict()
    dataset['vdi'] = vdi
    dataset['dimensionless'] = dimensionless
    dataset['narrowband'] = narrowband

    return jsonify(dataset)


@app.route('/analysis_results', methods=['GET', 'POST'])
def analysis_results():
    if request.method == 'GET':
        return render_template('submit.html')
    farm_name = request.form.get('farm_name')
    wind_turbine_name = request.form.get('wind_turbine_name')
    point_name = request.form.get('point_name')
    date = datetime.datetime.now().strftime('%Y-%m')
    record_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    sampling_time = request.form.get('sampling_time')
    analyst = request.form.get('analyst')
    ts = request.form.get('ts')
    freq = request.form.get('freq')
    env = request.form.get('env')
    trend = request.form.get('trend')
    level = request.form.get('level')
    img_t = request.form.get('img_t')
    img_f = request.form.get('img_f')
    img_e = request.form.get('img_e')
    img_1 = request.form.get('img_1')
    img_2 = request.form.get('img_2')
    img_3 = request.form.get('img_3')
    img_4 = request.form.get('img_4')

    collection = local[farm_name]['analysis_results']

    query = {'farm_name': farm_name, 'wind_turbine_name': wind_turbine_name, 'date': date}

    dataset = collection.find_one(query)
    if not dataset:
        dataset = {}

    if point_name not in dataset.keys():
        mp_data = []
    else:
        mp_data = dataset[point_name]

    data = {
        'record_time': record_time,
        'sampling_time': sampling_time,
        'analyst': analyst,
        'ts': ts,
        'freq': freq,
        'env': env,
        'trend': trend,
        'level': level,
        'img_t': img_t,
        'img_f': img_f,
        'img_e': img_e,
        'img_1': img_1,
        'img_2': img_2,
        'img_3': img_3,
        'img_4': img_4,
    }

    mp_data.append(data)

    dataset.update({point_name: mp_data})

    collection.update_one(query, {'$set': dataset}, upsert=True)

    return jsonify({'status': 'success'})


@app.route('/query')
def query():
    return render_template('query.html')


@app.route('/get_results', methods=['POST'])
def get_results():
    farm_name = request.form.get('farm_name')
    wind_turbine_name = request.form.get('wind_turbine_name')
    date = request.form.get('date')

    collection = local[farm_name]['analysis_results']

    query = {'farm_name': farm_name, 'wind_turbine_name': wind_turbine_name, 'date': date}

    dataset = collection.find_one(query)
    dataset['_id'] = str(dataset['_id'])

    return jsonify(dataset)


@app.route('/preview')
def preview():
    return render_template('preview.html')


@app.route('/merge')
def merge():
    return render_template('merge.html')


# 当把图片保存到磁盘，并用图片的磁盘路径作为img的src属性时，启用以下代码
@app.route('/get_picture_files', methods=['POST'])
def get_picture_files():
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    flag = request.form.get('flag')
    if flag == 'preview':
        path = r'temp/preview'
        # 获取图片的md5值
        md5 = get_picture_md5(path)

        img_t = request.form.get('img_t')
        img_f = request.form.get('img_f')
        img_e = request.form.get('img_e')

        img_t = img_t.split(',')[-1]
        img_f = img_f.split(',')[-1]
        img_e = img_e.split(',')[-1]

        img_t_data = base64.b64decode(img_t)
        img_f_data = base64.b64decode(img_f)
        img_e_data = base64.b64decode(img_e)

        img_t_md5 = hashlib.md5(img_t_data).hexdigest()
        img_f_md5 = hashlib.md5(img_f_data).hexdigest()
        img_e_md5 = hashlib.md5(img_e_data).hexdigest()

        # 通过比较图片hash值判断图片是否已经保存过
        if img_t_md5 in md5:
            img_t_name = md5[img_t_md5]
        else:
            img_t_name = 'img_t_'+now+'.png'

            with open(os.path.join(path, img_t_name), 'wb') as f:
                f.write(img_t_data)
        if img_f_md5 in md5:
            img_f_name = md5[img_f_md5]
        else:
            img_f_name = 'img_f_'+now+'.png'

            with open(os.path.join(path, img_f_name), 'wb') as f:
                f.write(img_f_data)
        if img_e_md5 in md5:
            img_e_name = md5[img_e_md5]
        else:
            img_e_name = 'img_e_'+now+'.png'

            with open(os.path.join(path, img_e_name), 'wb') as f:
                f.write(img_e_data)

        dataset = {
            'img_t_name': img_t_name,
            'img_f_name': img_f_name,
            'img_e_name': img_e_name,
        }

        return jsonify(dataset)
    if flag == 'merge':
        path = r'temp/merge'
        # 获取图片的md5值
        md5 = get_picture_md5(path)

        img_names = []
        records = request.form.get('records')
        records = json.loads(records)
        for i, record in enumerate(records):
            img_t = record[1]['img_t']
            img_f = record[1]['img_f']
            img_e = record[1]['img_e']

            img_t = img_t.split(',')[-1]
            img_f = img_f.split(',')[-1]
            img_e = img_e.split(',')[-1]

            img_t_data = base64.b64decode(img_t)
            img_f_data = base64.b64decode(img_f)
            img_e_data = base64.b64decode(img_e)

            img_t_md5 = hashlib.md5(img_t_data).hexdigest()
            img_f_md5 = hashlib.md5(img_f_data).hexdigest()
            img_e_md5 = hashlib.md5(img_e_data).hexdigest()

            temp = []

            # 通过比较图片hash值判断图片是否已经保存过
            if img_t_md5 in md5:
                img_t_name = md5[img_t_md5]
            else:
                img_t_name = 'img_t_'+str(i)+'_'+now+'.png'

                with open(os.path.join(path, img_t_name), 'wb') as f:
                    f.write(img_t_data)
            if img_f_md5 in md5:
                img_f_name = md5[img_f_md5]
            else:
                img_f_name = 'img_f_' + str(i) + '_' + now + '.png'

                with open(os.path.join(path, img_f_name), 'wb') as f:
                    f.write(img_f_data)
            if img_e_md5 in md5:
                img_e_name = md5[img_e_md5]
            else:
                img_e_name = 'img_e_'+str(i)+'_'+now+'.png'

                with open(os.path.join(path, img_e_name), 'wb') as f:
                    f.write(img_e_data)

            temp.append(img_t_name)
            temp.append(img_f_name)
            temp.append(img_e_name)
            img_names.append(temp)

        return jsonify({'img_names': img_names})

    return jsonify({'status': 'success'})


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)


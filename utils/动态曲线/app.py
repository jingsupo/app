# -*- coding: utf-8 -*-

from flask import Flask, render_template, jsonify
import datetime
import pandas as pd
import pymongo


# 建立mongodb数据库连接
conn = pymongo.MongoClient(host='localhost', port=27017)
# 建立风机数据库fengji
db = conn.fengji

app = Flask(__name__, template_folder='.')

@app.route('/getdata')
def getdata():
    data = pd.DataFrame(db['11'].find({},{'_id':0,'传感器1':1}).limit(2000))

    dataset = []
    for v in zip(range(len(data)), data.values.flatten()):
        d = {}
        d['name'] = 'haha'
        d['value'] = v
        dataset.append(d)

    return jsonify(dataset)

@app.route("/")
def index():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template("echarts.html", time=now)


if __name__ == "__main__":
    app.run(debug=True)

# -*- coding: utf-8 -*-

from flask import Flask, render_template, jsonify
from pyecharts import options as opts
from pyecharts.charts import Line
import pymongo
import pandas as pd
import datetime


# 建立mongodb数据库连接
conn = pymongo.MongoClient(host='localhost', port=27017)
# 建立风机数据库fengji
db = conn.fengji

app = Flask(__name__, template_folder='.')

@app.route('/getdata')
def getdata():
    data = pd.DataFrame(db.c11.find({},{'_id':0,'传感器1':1}).limit(2000))

    dt = []    
    for i in zip(range(len(data)), data.values.flatten()):
        dct = {}
        dct['name'] = 'haha'
        dct['value'] = i
        dt.append(dct)

    return jsonify(dt)

@app.route("/")
def index():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template("Awesome-pyecharts.html", time=now)


if __name__ == "__main__":
    app.run(debug=True)

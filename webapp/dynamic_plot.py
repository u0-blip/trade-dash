from pandas_datareader import data
import datetime
from bokeh.plotting import figure, show, output_file
from bokeh.embed import components
from bokeh.resources import CDN
from flask import Blueprint
import numpy as np

from flask import Flask, render_template, flash, request, url_for, jsonify, session, redirect, send_file
from wtforms import Form, TextField, validators, StringField, SubmitField, fields, FormField

plot_page = Blueprint('plot_page', __name__, template_folder='templates')


@plot_page.route('/plot',methods =['GET','POST'])
def plot():
    start = datetime.datetime(2020,5,1)
    end = datetime.datetime.today().strftime("%Y/%m/%d")
    # word = request.form['company_ip']

    # df=data.DataReader(name=word,data_source="iex",start=start,end=end, api_key='pk_c88b455c96e54a6b965aa23c1797f5ad')
    import pandas_datareader as pdr
    df=pdr.get_data_yahoo('AAPL', start=start, end=end, interval='d')

    def inc_dec(c, o):
        if c > o:
            value="Increase"
        elif c < o:
            value="Decrease"
        else:
            value="Equal"
        return value

    # print('head', df.head())
    # print(len(df))

    df["Status"]=[inc_dec(c,o) for c, o in zip(df.Close,df.Open)]
    df["Middle"]=(df.Open+df.Close)/2
    df["Height"]=abs(df.Close-df.Open)

    p=figure(x_axis_type='datetime', width=1000, height=300)
    p.title.text="Candlestick Chart"
    p.grid.grid_line_alpha=0.3

    hours_12=12*60*60*1000

    p.segment(df.index, df.High, df.index, df.Low, color="Black")

    p.rect(df.index[df.Status=="Increase"],df.Middle[df.Status=="Increase"],
           hours_12, df.Height[df.Status=="Increase"],fill_color="#CCFFFF",line_color="black")

    p.rect(df.index[df.Status=="Decrease"],df.Middle[df.Status=="Decrease"],
           hours_12, df.Height[df.Status=="Decrease"],fill_color="#FF3333",line_color="black")


    script1, div1 = components(p)
    cdn_js=CDN.js_files[0]
    # cdn_css=CDN.css_files[0]
    predicted = predict_prices(df.Middle[-10:].values.reshape(-1, 1), np.expand_dims(np.arange(29), 1))
    # print(predicted)
    # print(predicted, script1, div1, cdn_js)
    return render_template("plot.html",
    script1=script1,
    predicted = predicted,
    div1=div1,
    # cdn_css=cdn_css,
    cdn_js=cdn_js )

def predict_prices(prices,x):
    from sklearn.svm import SVR
    import numpy as np
    
    dates = list(range(len(prices)))
    dates = np.reshape(dates,(len(dates),1))
    svr_rbf = SVR(kernel = 'rbf',C=1e3,gamma=0.1)
    svr_rbf.fit(dates,prices)

    return svr_rbf.predict(x)[0]

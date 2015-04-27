#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'


from flask import Flask, render_template

app = Flask(__name__)

# config
app.config.from_pyfile('config.py')
app.template_folder = app.config['TEMPLATES']
app.static_folder = app.config['STATIC']



@app.route('/')
def index():
    return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=True)
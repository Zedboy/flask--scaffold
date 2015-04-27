#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

from flask import render_template
from avatar import app


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload')
def upload():

    return render_template('upload.html')



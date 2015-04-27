#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'


from flask import Flask

app = Flask(__name__)

# config
app.config.from_pyfile('config.py')
app.template_folder = app.config['TEMPLATES']
app.static_folder = app.config['STATIC']

import views


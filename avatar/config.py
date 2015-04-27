#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'


import os


DEBUG = True
APPDIR = os.path.abspath(os.path.dirname(__file__))
STATIC = os.path.join(APPDIR, 'static')
TEMPLATES = os.path.join(APPDIR, 'templates')
SECRET_KEY = 'you-will-never-guess'
